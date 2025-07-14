"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: mcp_service.py                                                        │
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

from typing import Any, Dict, List, Optional, Tuple
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
    SseServerParams,
)
from contextlib import AsyncExitStack
import os
from src.utils.logger import setup_logger
from src.services.mcp_server_service import get_mcp_server
from sqlalchemy.orm import Session

logger = setup_logger(__name__)


class MCPService:
    def __init__(self):
        self.tools = []
        self.exit_stack = AsyncExitStack()

    async def _connect_to_mcp_server(
        self, server_config: Dict[str, Any]
    ) -> Tuple[List[Any], Optional[AsyncExitStack]]:
        """Connect to a specific MCP server and return its tools."""
        try:
            # Determines the type of server (local or remote)
            if "url" in server_config:
                # Remote server (SSE)
                connection_params = SseServerParams(
                    url=server_config["url"], headers=server_config.get("headers", {})
                )
            else:
                # Local server (Stdio)
                command = server_config.get("command", "npx")
                args = server_config.get("args", [])

                # Adds environment variables if specified
                env = server_config.get("env", {})
                if env:
                    for key, value in env.items():
                        os.environ[key] = value

                connection_params = StdioServerParameters(
                    command=command, args=args, env=env
                )

            tools, exit_stack = await MCPToolset.from_server(
                connection_params=connection_params
            )

            return tools, exit_stack

        except Exception as e:
            logger.error(f"Error connecting to MCP server: {e}")
            return [], None

    def _filter_incompatible_tools(self, tools: List[Any]) -> List[Any]:
        """Filters incompatible tools with the model."""
        problematic_tools = [
            "create_pull_request_review",  # This tool causes the 400 INVALID_ARGUMENT error
        ]

        filtered_tools = []
        removed_count = 0

        for tool in tools:
            if tool.name in problematic_tools:
                logger.warning(f"Removing incompatible tool: {tool.name}")
                removed_count += 1
            else:
                filtered_tools.append(tool)

        if removed_count > 0:
            logger.warning(f"Removed {removed_count} incompatible tools.")

        return filtered_tools

    def _filter_tools_by_agent(
        self, tools: List[Any], agent_tools: List[str]
    ) -> List[Any]:
        """Filters tools compatible with the agent."""
        if not agent_tools or len(agent_tools) == 0:
            return tools

        filtered_tools = []
        for tool in tools:
            logger.info(f"Tool: {tool.name}")
            if tool.name in agent_tools:
                filtered_tools.append(tool)
        return filtered_tools

    async def build_tools(
        self, mcp_config: Dict[str, Any], db: Session
    ) -> Tuple[List[Any], AsyncExitStack]:
        """Builds a list of tools from multiple MCP servers."""
        self.tools = []
        self.exit_stack = AsyncExitStack()

        try:
            mcp_servers = mcp_config.get("mcp_servers", [])
            if mcp_servers is not None:
                # Process each MCP server in the configuration
                for server in mcp_servers:
                    try:
                        # Search for the MCP server in the database
                        mcp_server = get_mcp_server(db, server["id"])
                        if not mcp_server:
                            logger.warning(f"MCP Server not found: {server['id']}")
                            continue

                        # Prepares the server configuration
                        server_config = mcp_server.config_json.copy()

                        # Replaces the environment variables in the config_json
                        if "env" in server_config and server_config["env"] is not None:
                            for key, value in server_config["env"].items():
                                if value and value.startswith("env@@"):
                                    env_key = value.replace("env@@", "")
                                    if server.get("envs") and env_key in server.get(
                                        "envs", {}
                                    ):
                                        server_config["env"][key] = server["envs"][
                                            env_key
                                        ]
                                    else:
                                        logger.warning(
                                            f"Environment variable '{env_key}' not provided for the MCP server {mcp_server.name}"
                                        )
                                        continue

                        logger.info(f"Connecting to MCP server: {mcp_server.name}")
                        tools, exit_stack = await self._connect_to_mcp_server(
                            server_config
                        )

                        if tools and exit_stack:
                            # Filters incompatible tools
                            filtered_tools = self._filter_incompatible_tools(tools)

                            # Filters tools compatible with the agent
                            agent_tools = server.get("tools", [])
                            if agent_tools:
                                filtered_tools = self._filter_tools_by_agent(
                                    filtered_tools, agent_tools
                                )
                            self.tools.extend(filtered_tools)

                            # Registers the exit_stack with the AsyncExitStack
                            await self.exit_stack.enter_async_context(exit_stack)
                            logger.info(
                                f"MCP Server {mcp_server.name} connected successfully. Added {len(filtered_tools)} tools."
                            )
                        else:
                            logger.warning(
                                f"Failed to connect or no tools available for {mcp_server.name}"
                            )

                    except Exception as e:
                        logger.error(
                            f"Error connecting to MCP server {server.get('id', 'unknown')}: {e}"
                        )
                        continue

            custom_mcp_servers = mcp_config.get("custom_mcp_servers", [])
            if custom_mcp_servers is not None:
                # Process custom MCP servers
                for server in custom_mcp_servers:
                    if not server:
                        logger.warning(
                            "Empty server configuration found in custom_mcp_servers"
                        )
                        continue

                    try:
                        logger.info(
                            f"Connecting to custom MCP server: {server.get('url', 'unknown')}"
                        )
                        tools, exit_stack = await self._connect_to_mcp_server(server)

                        if tools:
                            self.tools.extend(tools)
                        else:
                            logger.warning("No tools returned from custom MCP server")
                            continue

                        if exit_stack:
                            await self.exit_stack.enter_async_context(exit_stack)
                            logger.info(
                                f"Custom MCP server connected successfully. Added {len(tools)} tools."
                            )
                        else:
                            logger.warning(
                                "No exit_stack returned from custom MCP server"
                            )
                    except Exception as e:
                        logger.error(
                            f"Error connecting to custom MCP server {server.get('url', 'unknown')}: {e}"
                        )
                        continue

            logger.info(
                f"MCP Toolset created successfully. Total of {len(self.tools)} tools."
            )

        except Exception as e:
            # Ensure cleanup
            await self.exit_stack.aclose()
            logger.error(f"Fatal error connecting to MCP servers: {e}")
            # Recreate an empty exit_stack
            self.exit_stack = AsyncExitStack()

        return self.tools, self.exit_stack
