"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: agent_service.py                                                      │
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

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from src.models.models import Agent, AgentFolder, ApiKey
from src.schemas.schemas import AgentCreate
from typing import List, Optional, Dict, Any, Union
from src.services.mcp_server_service import get_mcp_server
import uuid
import logging
import httpx

logger = logging.getLogger(__name__)


# Helper function to generate API keys
def generate_api_key() -> str:
    """Generate a secure API key"""
    # Format: sk-proj-{random 64 chars}

    return str(uuid.uuid4())


def _convert_uuid_to_str(obj):
    """
    Recursively convert all UUID objects to strings in a dictionary, list or scalar value.
    This ensures JSON serialize for complex nested objects.
    """
    if isinstance(obj, dict):
        return {key: _convert_uuid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_uuid_to_str(item) for item in obj]
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    else:
        return obj


def validate_sub_agents(db: Session, sub_agents: List[Union[uuid.UUID, str]]) -> bool:
    """Validate if all sub-agents exist"""
    logger.info(f"Validating sub-agents: {sub_agents}")

    if not sub_agents:
        logger.warning("Empty sub-agents list")
        return False

    for agent_id in sub_agents:
        # Ensure the ID is in the correct format
        agent_id_str = str(agent_id)
        logger.info(f"Validating sub-agent with ID: {agent_id_str}")

        agent = get_agent(db, agent_id_str)
        if not agent:
            logger.warning(f"Sub-agent not found: {agent_id_str}")
            return False
        logger.info(f"Valid sub-agent: {agent.name} (ID: {agent_id_str})")

    logger.info(f"All {len(sub_agents)} sub-agents are valid")
    return True


def get_agent(db: Session, agent_id: Union[uuid.UUID, str]) -> Optional[Agent]:
    """Search for an agent by ID"""
    try:
        # Convert to UUID if it's a string
        if isinstance(agent_id, str):
            try:
                agent_id = uuid.UUID(agent_id)
            except ValueError:
                logger.warning(f"Invalid agent ID: {agent_id}")
                return None

        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            logger.warning(f"Agent not found: {agent_id}")
            return None

        # Sanitize agent name if it contains spaces or special characters
        if agent.name and any(c for c in agent.name if not (c.isalnum() or c == "_")):
            agent.name = "".join(
                c if c.isalnum() or c == "_" else "_" for c in agent.name
            )
            # Update in database
            db.commit()

        return agent
    except SQLAlchemyError as e:
        logger.error(f"Error searching for agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for agent",
        )


def get_agents_by_client(
    db: Session,
    client_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    folder_id: Optional[uuid.UUID] = None,
    sort_by: str = "name",
    sort_direction: str = "asc",
) -> List[Agent]:
    """Search for agents by client with pagination and optional folder filter"""
    try:
        query = db.query(Agent).filter(Agent.client_id == client_id)

        # Filter by folder if specified
        if folder_id is not None:
            query = query.filter(Agent.folder_id == folder_id)

        # Apply sorting
        if sort_by == "name":
            if sort_direction.lower() == "desc":
                query = query.order_by(Agent.name.desc())
            else:
                query = query.order_by(Agent.name)
        elif sort_by == "created_at":
            if sort_direction.lower() == "desc":
                query = query.order_by(Agent.created_at.desc())
            else:
                query = query.order_by(Agent.created_at)

        agents = query.offset(skip).limit(limit).all()

        # Sanitize agent names if they contain spaces or special characters
        for agent in agents:
            if agent.name and any(
                c for c in agent.name if not (c.isalnum() or c == "_")
            ):
                agent.name = "".join(
                    c if c.isalnum() or c == "_" else "_" for c in agent.name
                )
                # Update in database
                db.commit()

        return agents
    except SQLAlchemyError as e:
        logger.error(f"Error searching for client agents {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for agents",
        )


async def create_agent(db: Session, agent: AgentCreate) -> Agent:
    """Create a new agent"""
    try:
        # Special handling for a2a type agents
        if agent.type == "a2a":
            if not agent.agent_card_url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="agent_card_url is required for a2a type agents",
                )

            try:
                # Fetch agent card information
                async with httpx.AsyncClient() as client:
                    response = await client.get(agent.agent_card_url)
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to fetch agent card: HTTP {response.status_code}",
                        )
                    agent_card = response.json()

                # Update agent with information from agent card
                # Only update name if not provided or empty, or sanitize it
                if not agent.name or agent.name.strip() == "":
                    # Sanitize name: remove spaces and special characters
                    card_name = agent_card.get("name", "Unknown Agent")
                    sanitized_name = "".join(
                        c if c.isalnum() or c == "_" else "_" for c in card_name
                    )
                    agent.name = sanitized_name

                agent.description = agent_card.get("description", "")

                if agent.config is None:
                    agent.config = {}

                # Store the whole agent card in config
                if isinstance(agent.config, dict):
                    agent.config["agent_card"] = agent_card
                else:
                    agent.config = {"agent_card": agent_card}

            except Exception as e:
                logger.error(f"Error fetching agent card: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to process agent card: {str(e)}",
                )

        elif agent.type == "workflow":
            if not isinstance(agent.config, dict):
                agent.config = {}

            if "api_key" not in agent.config or not agent.config["api_key"]:
                agent.config["api_key"] = generate_api_key()

        elif agent.type == "task":
            if not isinstance(agent.config, dict):
                agent.config = {}
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid configuration: must be an object with tasks",
                )

            if "tasks" not in agent.config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid configuration: tasks is required for {agent.type} agents",
                )

            if not agent.config["tasks"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid configuration: tasks cannot be empty",
                )

            for task in agent.config["tasks"]:
                if "agent_id" not in task:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Each task must have an agent_id",
                    )

                agent_id = task["agent_id"]
                task_agent = get_agent(db, agent_id)
                if not task_agent:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Agent not found for task: {agent_id}",
                    )

            if "sub_agents" in agent.config and agent.config["sub_agents"]:
                if not validate_sub_agents(db, agent.config["sub_agents"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One or more sub-agents do not exist",
                    )

            if "api_key" not in agent.config or not agent.config["api_key"]:
                agent.config["api_key"] = generate_api_key()

        # Additional sub-agent validation (for non-llm and non-a2a types)
        elif agent.type != "llm":
            if not isinstance(agent.config, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid configuration: must be an object with sub_agents",
                )

            if "sub_agents" not in agent.config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid configuration: sub_agents is required for sequential, parallel or loop agents",
                )

            if not agent.config["sub_agents"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid configuration: sub_agents cannot be empty",
                )

            if not validate_sub_agents(db, agent.config["sub_agents"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more sub-agents do not exist",
                )

        # Process the configuration before creating the agent
        config = agent.config
        if config is None:
            config = {}
            agent.config = config

        # Ensure config is a dictionary
        if not isinstance(config, dict):
            config = {}
            agent.config = config

        # Generate automatic API key if not provided or empty
        if not config.get("api_key") or config.get("api_key") == "":
            logger.info("Generating automatic API key for new agent")
            config["api_key"] = generate_api_key()

        processed_config = {}
        processed_config["api_key"] = config.get("api_key", "")

        if "tools" in config:
            processed_config["tools"] = config["tools"]

        if "custom_tools" in config:
            processed_config["custom_tools"] = config["custom_tools"]

        if "agent_tools" in config:
            processed_config["agent_tools"] = config["agent_tools"]

        if "sub_agents" in config:
            processed_config["sub_agents"] = config["sub_agents"]

        if "custom_mcp_servers" in config:
            processed_config["custom_mcp_servers"] = config["custom_mcp_servers"]

        for key, value in config.items():
            if key not in [
                "api_key",
                "tools",
                "custom_tools",
                "sub_agents",
                "agent_tools",
                "custom_mcp_servers",
                "mcp_servers",
            ]:
                processed_config[key] = value

        # Process MCP servers
        if "mcp_servers" in config and config["mcp_servers"] is not None:
            processed_servers = []
            for server in config["mcp_servers"]:
                # Convert server id to UUID if it's a string
                server_id = server["id"]
                if isinstance(server_id, str):
                    server_id = uuid.UUID(server_id)

                # Search for MCP server in the database
                mcp_server = get_mcp_server(db, server_id)
                if not mcp_server:
                    raise HTTPException(
                        status_code=400,
                        detail=f"MCP server not found: {server['id']}",
                    )

                # Check if all required environment variables are provided
                for env_key, env_value in mcp_server.environments.items():
                    if env_key not in server.get("envs", {}):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Environment variable '{env_key}' not provided for MCP server {mcp_server.name}",
                        )

                # Add the processed server
                processed_servers.append(
                    {
                        "id": str(server["id"]),
                        "envs": server["envs"],
                        "tools": server["tools"],
                    }
                )

            processed_config["mcp_servers"] = processed_servers
        elif "mcp_servers" in config:
            processed_config["mcp_servers"] = config["mcp_servers"]

        # Process custom MCP servers
        if "custom_mcp_servers" in config and config["custom_mcp_servers"] is not None:
            processed_custom_servers = []
            for server in config["custom_mcp_servers"]:
                # Validate URL format
                if not server.get("url"):
                    raise HTTPException(
                        status_code=400,
                        detail="URL is required for custom MCP servers",
                    )

                # Add the custom server
                processed_custom_servers.append(
                    {"url": server["url"], "headers": server.get("headers", {})}
                )

            processed_config["custom_mcp_servers"] = processed_custom_servers

        # Process sub-agents
        if "sub_agents" in config and config["sub_agents"] is not None:
            processed_config["sub_agents"] = [
                str(agent_id) for agent_id in config["sub_agents"]
            ]

        # Process agent tools
        if "agent_tools" in config and config["agent_tools"] is not None:
            processed_config["agent_tools"] = [
                str(agent_id) for agent_id in config["agent_tools"]
            ]

        # Process tools
        if "tools" in config and config["tools"] is not None:
            processed_tools = []
            for tool in config["tools"]:
                # Convert tool id to string
                tool_id = tool["id"]

                envs = tool.get("envs", {})
                if envs is None:
                    envs = {}

                processed_tools.append({"id": str(tool_id), "envs": envs})
            processed_config["tools"] = processed_tools

        agent.config = processed_config

        # Ensure all config objects are serializable (convert UUIDs to strings)
        if agent.config is not None:
            agent.config = _convert_uuid_to_str(agent.config)

        # Convert agent to dict ensuring all UUIDs are converted to strings
        agent_dict = agent.model_dump()
        agent_dict = _convert_uuid_to_str(agent_dict)

        # Create agent from the processed dictionary
        db_agent = Agent(**agent_dict)

        # Make one final check to ensure all nested objects are serializable
        # (especially nested UUIDs in config)
        if db_agent.config is not None:
            db_agent.config = _convert_uuid_to_str(db_agent.config)

        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        logger.info(f"Agent created successfully: {db_agent.id}")

        return db_agent
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating agent: {str(e)}")

        # Add debugging info
        try:
            import json

            if "agent_dict" in locals():
                agent_json = json.dumps(agent_dict)
                logger.info(f"Agent creation attempt with: {agent_json[:200]}...")
        except Exception as json_err:
            logger.error(f"Could not serialize agent for debugging: {str(json_err)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent: {str(e)}",
        )


async def update_agent(
    db: Session, agent_id: uuid.UUID, agent_data: Dict[str, Any]
) -> Agent:
    """Update an existing agent"""
    try:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Check if api_key_id is defined
        if "api_key_id" in agent_data and agent_data["api_key_id"]:
            # Check if the referenced API key exists
            api_key_id = agent_data["api_key_id"]
            if isinstance(api_key_id, str):
                api_key_id = uuid.UUID(api_key_id)

            api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail=f"API Key with ID {api_key_id} not found",
                )

            # Check if the key belongs to the agent's client
            if api_key.client_id != agent.client_id:
                raise HTTPException(
                    status_code=403,
                    detail="API Key does not belong to the same client as the agent",
                )

        # Continue with the original code
        if "type" in agent_data and agent_data["type"] == "a2a":
            if "agent_card_url" not in agent_data or not agent_data["agent_card_url"]:
                raise HTTPException(
                    status_code=400,
                    detail="agent_card_url is required for a2a type agents",
                )

            if not agent_data["agent_card_url"].endswith("/.well-known/agent.json"):
                raise HTTPException(
                    status_code=400,
                    detail="agent_card_url must end with /.well-known/agent.json",
                )

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(agent_data["agent_card_url"])
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to fetch agent card: HTTP {response.status_code}",
                        )
                    agent_card = response.json()

                # Only update name if the original update doesn't specify a name
                if "name" not in agent_data or not agent_data["name"].strip():
                    # Sanitize name: remove spaces and special characters
                    card_name = agent_card.get("name", "Unknown Agent")
                    sanitized_name = "".join(
                        c if c.isalnum() or c == "_" else "_" for c in card_name
                    )
                    agent_data["name"] = sanitized_name
                agent_data["description"] = agent_card.get("description", "")

                if "config" not in agent_data or agent_data["config"] is None:
                    agent_data["config"] = agent.config if agent.config else {}

                agent_data["config"]["agent_card"] = agent_card

            except Exception as e:
                logger.error(f"Error fetching agent card: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to process agent card: {str(e)}",
                )

        elif "agent_card_url" in agent_data and agent.type == "a2a":
            if not agent_data["agent_card_url"]:
                raise HTTPException(
                    status_code=400,
                    detail="agent_card_url cannot be empty for a2a type agents",
                )

            if not agent_data["agent_card_url"].endswith("/.well-known/agent.json"):
                raise HTTPException(
                    status_code=400,
                    detail="agent_card_url must end with /.well-known/agent.json",
                )

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(agent_data["agent_card_url"])
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Failed to fetch agent card: HTTP {response.status_code}",
                        )
                    agent_card = response.json()

                # Only update name if the original update doesn't specify a name
                if "name" not in agent_data or not agent_data["name"].strip():
                    # Sanitize name: remove spaces and special characters
                    card_name = agent_card.get("name", "Unknown Agent")
                    sanitized_name = "".join(
                        c if c.isalnum() or c == "_" else "_" for c in card_name
                    )
                    agent_data["name"] = sanitized_name
                agent_data["description"] = agent_card.get("description", "")

                if "config" not in agent_data or agent_data["config"] is None:
                    agent_data["config"] = agent.config if agent.config else {}

                agent_data["config"]["agent_card"] = agent_card

            except Exception as e:
                logger.error(f"Error fetching agent card: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to process agent card: {str(e)}",
                )

        # Convert UUIDs to strings before saving
        if "config" in agent_data:
            config = agent_data["config"]

            processed_config = {}
            processed_config["api_key"] = config.get("api_key", "")

            if "tools" in config:
                processed_config["tools"] = config["tools"]

            if "custom_tools" in config:
                processed_config["custom_tools"] = config["custom_tools"]

            if "sub_agents" in config:
                processed_config["sub_agents"] = config["sub_agents"]

            if "agent_tools" in config:
                processed_config["agent_tools"] = config["agent_tools"]

            if "custom_mcp_servers" in config:
                processed_config["custom_mcp_servers"] = config["custom_mcp_servers"]

            for key, value in config.items():
                if key not in [
                    "api_key",
                    "tools",
                    "custom_tools",
                    "sub_agents",
                    "agent_tools",
                    "custom_mcp_servers",
                    "mcp_servers",
                ]:
                    processed_config[key] = value

            # Process MCP servers
            if "mcp_servers" in config and config["mcp_servers"] is not None:
                processed_servers = []
                for server in config["mcp_servers"]:
                    # Convert server id to UUID if it's a string
                    server_id = server["id"]
                    if isinstance(server_id, str):
                        server_id = uuid.UUID(server_id)

                    # Search for MCP server in the database
                    mcp_server = get_mcp_server(db, server_id)
                    if not mcp_server:
                        raise HTTPException(
                            status_code=400,
                            detail=f"MCP server not found: {server['id']}",
                        )

                    # Check if all required environment variables are provided
                    for env_key, env_value in mcp_server.environments.items():
                        if env_key not in server.get("envs", {}):
                            raise HTTPException(
                                status_code=400,
                                detail=f"Environment variable '{env_key}' not provided for MCP server {mcp_server.name}",
                            )

                    # Add the processed server
                    processed_servers.append(
                        {
                            "id": str(server["id"]),
                            "envs": server["envs"],
                            "tools": server["tools"],
                        }
                    )

                processed_config["mcp_servers"] = processed_servers
            elif "mcp_servers" in config:
                processed_config["mcp_servers"] = config["mcp_servers"]

            # Process custom MCP servers
            if (
                "custom_mcp_servers" in config
                and config["custom_mcp_servers"] is not None
            ):
                processed_custom_servers = []
                for server in config["custom_mcp_servers"]:
                    # Validate URL format
                    if not server.get("url"):
                        raise HTTPException(
                            status_code=400,
                            detail="URL is required for custom MCP servers",
                        )

                    # Add the custom server
                    processed_custom_servers.append(
                        {"url": server["url"], "headers": server.get("headers", {})}
                    )

                processed_config["custom_mcp_servers"] = processed_custom_servers

            # Process sub-agents
            if "sub_agents" in config and config["sub_agents"] is not None:
                processed_config["sub_agents"] = [
                    str(agent_id) for agent_id in config["sub_agents"]
                ]

            # Process agent tools
            if "agent_tools" in config and config["agent_tools"] is not None:
                processed_config["agent_tools"] = [
                    str(agent_id) for agent_id in config["agent_tools"]
                ]

            # Process tools
            if "tools" in config and config["tools"] is not None:
                processed_tools = []
                for tool in config["tools"]:
                    # Convert tool id to string
                    tool_id = tool["id"]

                    envs = tool.get("envs", {})
                    if envs is None:
                        envs = {}

                    processed_tools.append({"id": str(tool_id), "envs": envs})
                processed_config["tools"] = processed_tools

            agent_data["config"] = processed_config

        # Ensure all config objects are serializable (convert UUIDs to strings)
        if "config" in agent_data and agent_data["config"] is not None:
            agent_data["config"] = _convert_uuid_to_str(agent_data["config"])

        # Check if the agent has API key and generate one if not
        agent_config = agent.config or {}
        if "config" not in agent_data:
            agent_data["config"] = agent_config

        if ("type" in agent_data and agent_data["type"] in ["task"]) or (
            agent.type in ["task"] and "config" in agent_data
        ):
            config = agent_data.get("config", {})
            if "tasks" not in config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid configuration: tasks is required for {agent_data.get('type', agent.type)} agents",
                )

            if not config["tasks"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid configuration: tasks cannot be empty",
                )

            for task in config["tasks"]:
                if "agent_id" not in task:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Each task must have an agent_id",
                    )

                agent_id = task["agent_id"]
                task_agent = get_agent(db, agent_id)
                if not task_agent:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Agent not found for task: {agent_id}",
                    )

            # Validar sub_agents se existir
            if "sub_agents" in config and config["sub_agents"]:
                if not validate_sub_agents(db, config["sub_agents"]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One or more sub-agents do not exist",
                    )

        if not agent_config.get("api_key") and (
            "config" not in agent_data or not agent_data["config"].get("api_key")
        ):
            logger.info(f"Generating missing API key for existing agent: {agent_id}")
            if "config" not in agent_data:
                agent_data["config"] = {}
            agent_data["config"]["api_key"] = generate_api_key()

        for key, value in agent_data.items():
            setattr(agent, key, value)

        db.commit()
        db.refresh(agent)
        return agent
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating agent: {str(e)}")


def delete_agent(db: Session, agent_id: uuid.UUID) -> bool:
    """Remove an agent from the database"""
    try:
        db_agent = get_agent(db, agent_id)
        if not db_agent:
            return False

        # Actually delete the agent from the database
        db.delete(db_agent)
        db.commit()
        logger.info(f"Agent deleted successfully: {agent_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting agent",
        )


def activate_agent(db: Session, agent_id: uuid.UUID) -> bool:
    """Reactivate an agent"""
    try:
        db_agent = get_agent(db, agent_id)
        if not db_agent:
            return False

        db.commit()
        logger.info(f"Agent reactivated successfully: {agent_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error reactivating agent {agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reactivating agent",
        )


# Functions for agent folders
def create_agent_folder(
    db: Session, client_id: uuid.UUID, name: str, description: Optional[str] = None
) -> AgentFolder:
    """Create a new folder to organize agents"""
    try:
        folder = AgentFolder(client_id=client_id, name=name, description=description)
        db.add(folder)
        db.commit()
        db.refresh(folder)
        logger.info(f"Agent folder created successfully: {folder.id}")
        return folder
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating agent folder: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent folder: {str(e)}",
        )


def get_agent_folder(db: Session, folder_id: uuid.UUID) -> Optional[AgentFolder]:
    """Search for an agent folder by ID"""
    try:
        return db.query(AgentFolder).filter(AgentFolder.id == folder_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error searching for agent folder {folder_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for agent folder",
        )


def get_agent_folders_by_client(
    db: Session, client_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[AgentFolder]:
    """List the agent folders of a client"""
    try:
        return (
            db.query(AgentFolder)
            .filter(AgentFolder.client_id == client_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        logger.error(f"Error listing agent folders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing agent folders",
        )


def update_agent_folder(
    db: Session,
    folder_id: uuid.UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[AgentFolder]:
    """Update an agent folder"""
    try:
        folder = get_agent_folder(db, folder_id)
        if not folder:
            return None

        if name is not None:
            folder.name = name
        if description is not None:
            folder.description = description

        db.commit()
        db.refresh(folder)
        logger.info(f"Agent folder updated: {folder_id}")
        return folder
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating agent folder {folder_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating agent folder",
        )


def delete_agent_folder(db: Session, folder_id: uuid.UUID) -> bool:
    """Remove an agent folder and unassign the agents"""
    try:
        folder = get_agent_folder(db, folder_id)
        if not folder:
            return False

        # Unassign the agents from the folder (do not delete the agents)
        agents = db.query(Agent).filter(Agent.folder_id == folder_id).all()
        for agent in agents:
            agent.folder_id = None

        # Delete the folder
        db.delete(folder)
        db.commit()
        logger.info(f"Agent folder removed: {folder_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error removing agent folder {folder_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing agent folder",
        )


def assign_agent_to_folder(
    db: Session, agent_id: uuid.UUID, folder_id: Optional[uuid.UUID]
) -> Optional[Agent]:
    """Assign an agent to a folder (or remove from folder if folder_id is None)"""
    try:
        agent = get_agent(db, agent_id)
        if not agent:
            return None

        # If folder_id is None, remove the agent from the current folder
        if folder_id is None:
            agent.folder_id = None
            db.commit()
            db.refresh(agent)
            logger.info(f"Agent removed from folder: {agent_id}")
            return agent

        # Verify if the folder exists
        folder = get_agent_folder(db, folder_id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Folder not found",
            )

        # Verify if the folder belongs to the same client as the agent
        if folder.client_id != agent.client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The folder must belong to the same client as the agent",
            )

        # Assign the agent to the folder
        agent.folder_id = folder_id
        db.commit()
        db.refresh(agent)
        logger.info(f"Agent assigned to folder: {folder_id}")
        return agent
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error assigning agent to folder: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error assigning agent to folder",
        )


def get_agents_by_folder(
    db: Session, folder_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[Agent]:
    """List the agents of a specific folder"""
    try:
        return (
            db.query(Agent)
            .filter(Agent.folder_id == folder_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        logger.error(f"Error listing agents of folder {folder_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing agents of folder",
        )


async def import_agents_from_json(
    db: Session,
    agents_data: Dict[str, Any],
    client_id: uuid.UUID,
    folder_id: Optional[uuid.UUID] = None,
) -> List[Agent]:
    """
    Import one or more agents from JSON data

    Args:
        db (Session): Database session
        agents_data (Dict[str, Any]): JSON data containing agent definitions
        client_id (uuid.UUID): Client ID to associate with the imported agents
        folder_id (Optional[uuid.UUID]): Optional folder ID to assign agents to

    Returns:
        List[Agent]: List of imported agents
    """
    # Check if the JSON contains a single agent or multiple agents
    if "agents" in agents_data:
        # Multiple agents import
        agents_list = agents_data["agents"]
        if not isinstance(agents_list, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The 'agents' field must contain a list of agent definitions",
            )
    else:
        # Single agent import
        agents_list = [agents_data]

    imported_agents = []
    errors = []
    id_mapping = {}  # Maps original IDs to newly created agent IDs

    # First pass: Import all non-workflow agents to establish ID mappings
    for agent_data in agents_list:
        # Skip workflow agents in the first pass, we'll handle them in the second pass
        if agent_data.get("type") == "workflow":
            continue

        try:
            # Store original ID if present for reference mapping
            original_id = None
            if "id" in agent_data:
                original_id = agent_data["id"]
                del agent_data["id"]  # Always create a new agent with new ID

            # Set the client ID for this agent if not provided
            if "client_id" not in agent_data:
                agent_data["client_id"] = str(client_id)
            else:
                # Ensure the provided client_id matches the authenticated client
                agent_client_id = uuid.UUID(agent_data["client_id"])
                if agent_client_id != client_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Cannot import agent for client ID {agent_client_id}",
                    )

            # Set folder_id if provided and not already set in the agent data
            if folder_id and "folder_id" not in agent_data:
                agent_data["folder_id"] = str(folder_id)

            # Process config: Keep original configuration intact except for agent references
            if "config" in agent_data and agent_data["config"]:
                config = agent_data["config"]

                # Process sub_agents if present
                if "sub_agents" in config and config["sub_agents"]:
                    processed_sub_agents = []

                    for sub_agent_id in config["sub_agents"]:
                        try:
                            # Check if agent exists in database
                            existing_agent = get_agent(db, sub_agent_id)
                            if existing_agent:
                                processed_sub_agents.append(str(existing_agent.id))
                            else:
                                logger.warning(
                                    f"Referenced sub_agent {sub_agent_id} not found - will be skipped"
                                )
                        except Exception as e:
                            logger.warning(
                                f"Error processing sub_agent {sub_agent_id}: {str(e)}"
                            )

                    config["sub_agents"] = processed_sub_agents

                # Process agent_tools if present
                if "agent_tools" in config and config["agent_tools"]:
                    processed_agent_tools = []

                    for agent_tool_id in config["agent_tools"]:
                        try:
                            # Check if agent exists in database
                            existing_agent = get_agent(db, agent_tool_id)
                            if existing_agent:
                                processed_agent_tools.append(str(existing_agent.id))
                            else:
                                logger.warning(
                                    f"Referenced agent_tool {agent_tool_id} not found - will be skipped"
                                )
                        except Exception as e:
                            logger.warning(
                                f"Error processing agent_tool {agent_tool_id}: {str(e)}"
                            )

                    config["agent_tools"] = processed_agent_tools

            # Convert to AgentCreate schema
            agent_create = AgentCreate(**agent_data)

            # Create the agent using existing create_agent function
            db_agent = await create_agent(db, agent_create)

            # Store mapping from original ID to new ID
            if original_id:
                id_mapping[original_id] = str(db_agent.id)

            # If folder_id is provided but not in agent_data (couldn't be set at creation time)
            # assign the agent to the folder after creation
            if folder_id and not agent_data.get("folder_id"):
                db_agent = assign_agent_to_folder(db, db_agent.id, folder_id)

            # Set agent card URL if needed
            if not db_agent.agent_card_url:
                db_agent.agent_card_url = db_agent.agent_card_url_property

            imported_agents.append(db_agent)

        except Exception as e:
            # Log the error and continue with other agents
            agent_name = agent_data.get("name", "Unknown")
            error_msg = f"Error importing agent '{agent_name}': {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

    # Second pass: Process workflow agents
    for agent_data in agents_list:
        # Only process workflow agents in the second pass
        if agent_data.get("type") != "workflow":
            continue

        try:
            # Store original ID if present for reference mapping
            original_id = None
            if "id" in agent_data:
                original_id = agent_data["id"]
                del agent_data["id"]  # Always create a new agent with new ID

            # Set the client ID for this agent if not provided
            if "client_id" not in agent_data:
                agent_data["client_id"] = str(client_id)
            else:
                # Ensure the provided client_id matches the authenticated client
                agent_client_id = uuid.UUID(agent_data["client_id"])
                if agent_client_id != client_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Cannot import agent for client ID {agent_client_id}",
                    )

            # Set folder_id if provided and not already set in the agent data
            if folder_id and "folder_id" not in agent_data:
                agent_data["folder_id"] = str(folder_id)

            # Process workflow nodes
            if "config" in agent_data and agent_data["config"]:
                config = agent_data["config"]

                # Process workflow nodes
                if "workflow" in config and config["workflow"]:
                    workflow = config["workflow"]

                    if "nodes" in workflow and isinstance(workflow["nodes"], list):
                        for node in workflow["nodes"]:
                            if (
                                isinstance(node, dict)
                                and node.get("type") == "agent-node"
                            ):
                                if "data" in node and "agent" in node["data"]:
                                    agent_node = node["data"]["agent"]

                                    # Store the original node ID
                                    node_agent_id = None
                                    if "id" in agent_node:
                                        node_agent_id = agent_node["id"]

                                        # Check if this ID is in our mapping (we created it in this import)
                                        if node_agent_id in id_mapping:
                                            # Use our newly created agent
                                            # Get the agent from database with the mapped ID
                                            mapped_id = uuid.UUID(
                                                id_mapping[node_agent_id]
                                            )
                                            db_agent = get_agent(db, mapped_id)
                                            if db_agent:
                                                # Replace with database agent definition
                                                # Extract agent data as dictionary
                                                agent_dict = {
                                                    "id": str(db_agent.id),
                                                    "name": db_agent.name,
                                                    "description": db_agent.description,
                                                    "role": db_agent.role,
                                                    "goal": db_agent.goal,
                                                    "type": db_agent.type,
                                                    "model": db_agent.model,
                                                    "instruction": db_agent.instruction,
                                                    "config": db_agent.config,
                                                }
                                                node["data"]["agent"] = agent_dict
                                        else:
                                            # Check if this agent exists in database
                                            try:
                                                existing_agent = get_agent(
                                                    db, node_agent_id
                                                )
                                                if existing_agent:
                                                    # Replace with database agent definition
                                                    # Extract agent data as dictionary
                                                    agent_dict = {
                                                        "id": str(existing_agent.id),
                                                        "name": existing_agent.name,
                                                        "description": existing_agent.description,
                                                        "role": existing_agent.role,
                                                        "goal": existing_agent.goal,
                                                        "type": existing_agent.type,
                                                        "model": existing_agent.model,
                                                        "instruction": existing_agent.instruction,
                                                        "config": existing_agent.config,
                                                    }
                                                    node["data"]["agent"] = agent_dict
                                                else:
                                                    # Agent doesn't exist, so we'll create a new one
                                                    # First, remove ID to get a new one
                                                    if "id" in agent_node:
                                                        del agent_node["id"]

                                                    # Set client_id to match parent
                                                    agent_node["client_id"] = str(
                                                        client_id
                                                    )

                                                    # Create agent
                                                    inner_agent_create = AgentCreate(
                                                        **agent_node
                                                    )
                                                    inner_db_agent = await create_agent(
                                                        db, inner_agent_create
                                                    )

                                                    # Replace with the new agent
                                                    # Extract agent data as dictionary
                                                    agent_dict = {
                                                        "id": str(inner_db_agent.id),
                                                        "name": inner_db_agent.name,
                                                        "description": inner_db_agent.description,
                                                        "role": inner_db_agent.role,
                                                        "goal": inner_db_agent.goal,
                                                        "type": inner_db_agent.type,
                                                        "model": inner_db_agent.model,
                                                        "instruction": inner_db_agent.instruction,
                                                        "config": inner_db_agent.config,
                                                    }
                                                    node["data"]["agent"] = agent_dict
                                            except Exception as e:
                                                logger.warning(
                                                    f"Error processing agent node {node_agent_id}: {str(e)}"
                                                )
                                                # Continue using the agent definition as is,
                                                # but without ID to get a new one
                                                if "id" in agent_node:
                                                    del agent_node["id"]
                                                agent_node["client_id"] = str(client_id)

                # Process sub_agents if present
                if "sub_agents" in config and config["sub_agents"]:
                    processed_sub_agents = []

                    for sub_agent_id in config["sub_agents"]:
                        # Check if agent exists in database
                        try:
                            # Check if this is an agent we just created
                            if sub_agent_id in id_mapping:
                                processed_sub_agents.append(id_mapping[sub_agent_id])
                            else:
                                # Check if this agent exists in database
                                existing_agent = get_agent(db, sub_agent_id)
                                if existing_agent:
                                    processed_sub_agents.append(str(existing_agent.id))
                                else:
                                    logger.warning(
                                        f"Referenced sub_agent {sub_agent_id} not found - will be skipped"
                                    )
                        except Exception as e:
                            logger.warning(
                                f"Error processing sub_agent {sub_agent_id}: {str(e)}"
                            )

                    config["sub_agents"] = processed_sub_agents

            # Convert to AgentCreate schema
            agent_create = AgentCreate(**agent_data)

            # Create the agent using existing create_agent function
            db_agent = await create_agent(db, agent_create)

            # Store mapping from original ID to new ID
            if original_id:
                id_mapping[original_id] = str(db_agent.id)

            # If folder_id is provided but not in agent_data (couldn't be set at creation time)
            # assign the agent to the folder after creation
            if folder_id and not agent_data.get("folder_id"):
                db_agent = assign_agent_to_folder(db, db_agent.id, folder_id)

            # Set agent card URL if needed
            if not db_agent.agent_card_url:
                db_agent.agent_card_url = db_agent.agent_card_url_property

            imported_agents.append(db_agent)

        except Exception as e:
            # Log the error and continue with other agents
            agent_name = agent_data.get("name", "Unknown")
            error_msg = f"Error importing agent '{agent_name}': {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

    # If no agents were imported successfully, raise an error
    if not imported_agents and errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Failed to import any agents", "errors": errors},
        )

    return imported_agents
