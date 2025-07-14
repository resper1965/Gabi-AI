"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: agent_builder.py                                                      │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: May 13, 2025                                                  │
│ Contact: contato@evolution-api.com                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ @copyright © Evolution API 2025. All rights reserved.                        │
│ Licensed under the Apache License, Version 2.0                               │
│                                                                              │
│ You may not use this file except in compliance with the License.             │
│ You may obtain a copy of the License at                                      │
│                                                                              │
│    http://www.apache.org/licenses/LICENSE-2.0                                │
│                                                                              │
│ Unless required by applicable law or agreed to in writing, software          │
│ distributed under the License is distributed on an "AS IS" BASIS,            │
│ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.     │
│ See the License for the specific language governing permissions and          │
│ limitations under the License.                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ @important                                                                   │
│ For any future changes to the code in this file, it is recommended to        │
│ include, together with the modification, the information of the developer    │
│ who changed it and the date of modification.                                 │
└──────────────────────────────────────────────────────────────────────────────┘
"""

from typing import List, Tuple, Optional
from src.schemas.schemas import Agent
from src.schemas.agent_config import AgentTask
from src.services.crewai.custom_tool import CustomToolBuilder
from src.services.crewai.mcp_service import MCPService
from src.utils.logger import setup_logger
from src.services.apikey_service import get_decrypted_api_key
from sqlalchemy.orm import Session
from contextlib import AsyncExitStack
from crewai import LLM, Agent as LlmAgent, Crew, Task, Process

from datetime import datetime
import uuid

logger = setup_logger(__name__)


class AgentBuilder:
    def __init__(self, db: Session):
        self.db = db
        self.custom_tool_builder = CustomToolBuilder()
        self.mcp_service = MCPService()

    async def _get_api_key(self, agent: Agent) -> str:
        """Get the API key for the agent."""
        api_key = None

        # Get API key from api_key_id
        if hasattr(agent, "api_key_id") and agent.api_key_id:
            if decrypted_key := get_decrypted_api_key(self.db, agent.api_key_id):
                logger.info(f"Using stored API key for agent {agent.name}")
                api_key = decrypted_key
            else:
                logger.error(f"Stored API key not found for agent {agent.name}")
                raise ValueError(
                    f"API key with ID {agent.api_key_id} not found or inactive"
                )
        else:
            # Check if there is an API key in the config (temporary field)
            config_api_key = agent.config.get("api_key") if agent.config else None
            if config_api_key:
                logger.info(f"Using config API key for agent {agent.name}")
                # Check if it is a UUID of a stored key
                try:
                    key_id = uuid.UUID(config_api_key)
                    if decrypted_key := get_decrypted_api_key(self.db, key_id):
                        logger.info("Config API key is a valid reference")
                        api_key = decrypted_key
                    else:
                        # Use the key directly
                        api_key = config_api_key
                except (ValueError, TypeError):
                    # It is not a UUID, use directly
                    api_key = config_api_key
            else:
                logger.error(f"No API key configured for agent {agent.name}")
                raise ValueError(
                    f"Agent {agent.name} does not have a configured API key"
                )

        return api_key

    async def _create_llm(self, agent: Agent) -> LLM:
        """Create an LLM from the agent data."""
        api_key = await self._get_api_key(agent)

        return LLM(model=agent.model, api_key=api_key)

    async def _create_llm_agent(
        self, agent: Agent, enabled_tools: List[str] = []
    ) -> Tuple[LlmAgent, Optional[AsyncExitStack]]:
        """Create an LLM agent from the agent data."""
        # Get custom tools from the configuration
        custom_tools = []
        custom_tools = self.custom_tool_builder.build_tools(agent.config)

        # # Get MCP tools from the configuration
        mcp_tools = []
        mcp_exit_stack = None
        if agent.config.get("mcp_servers") or agent.config.get("custom_mcp_servers"):
            try:
                mcp_tools, mcp_exit_stack = await self.mcp_service.build_tools(
                    agent.config, self.db
                )
            except Exception as e:
                logger.error(f"Error building MCP tools: {e}")
                # Continue without MCP tools
                mcp_tools = []
                mcp_exit_stack = None

        # # Get agent tools
        # agent_tools = await self._agent_tools_builder(agent)

        # Combine all tools
        all_tools = custom_tools + mcp_tools

        if enabled_tools:
            all_tools = [tool for tool in all_tools if tool.name in enabled_tools]
            logger.info(f"Enabled tools enabled. Total tools: {len(all_tools)}")

        now = datetime.now()
        current_datetime = now.strftime("%d/%m/%Y %H:%M")
        current_day_of_week = now.strftime("%A")
        current_date_iso = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        # Substitute variables in the prompt
        formatted_prompt = agent.instruction.format(
            current_datetime=current_datetime,
            current_day_of_week=current_day_of_week,
            current_date_iso=current_date_iso,
            current_time=current_time,
        )

        llm_agent = LlmAgent(
            role=agent.role,
            goal=agent.goal,
            backstory=formatted_prompt,
            llm=await self._create_llm(agent),
            tools=all_tools,
            verbose=True,
            cache=True,
            # memory=True,
        )

        return llm_agent, mcp_exit_stack

    async def _create_tasks(
        self, agent: LlmAgent, tasks: List[AgentTask] = []
    ) -> List[Task]:
        """Create tasks from the agent data."""
        tasks_list = []
        if tasks:
            tasks_list.extend(
                Task(
                    name=task.name,
                    description=task.description,
                    expected_output=task.expected_output,
                    agent=agent,
                    verbose=True,
                )
                for task in tasks
            )
        return tasks_list

    async def build_crew(self, agents: List[LlmAgent], tasks: List[Task] = []) -> Crew:
        """Create a crew from the agent data."""
        return Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

    async def build_llm_agent(
        self, root_agent, enabled_tools: List[str] = []
    ) -> Tuple[LlmAgent, Optional[AsyncExitStack]]:
        """Build an LLM agent with its sub-agents."""
        logger.info("Creating LLM agent")

        try:
            result = await self._create_llm_agent(root_agent, enabled_tools)

            if isinstance(result, tuple) and len(result) == 2:
                return result
            else:
                return result, None
        except Exception as e:
            logger.error(f"Error in build_llm_agent: {e}")
            raise

    async def build_agent(
        self, root_agent, enabled_tools: List[str] = []
    ) -> Tuple[LlmAgent, Optional[AsyncExitStack]]:
        """Build the appropriate agent based on the type of the root agent."""
        if root_agent.type == "llm":
            agent, exit_stack = await self.build_llm_agent(root_agent, enabled_tools)
            return agent, exit_stack
        elif root_agent.type == "a2a":
            raise ValueError("A2A agents are not supported yet")
            # return await self.build_a2a_agent(root_agent)
        elif root_agent.type == "workflow":
            raise ValueError("Workflow agents are not supported yet")
            # return await self.build_workflow_agent(root_agent)
        elif root_agent.type == "task":
            raise ValueError("Task agents are not supported yet")
            # return await self.build_task_agent(root_agent)
        else:
            raise ValueError(f"Invalid agent type: {root_agent.type}")
            # return await self.build_composite_agent(root_agent)
