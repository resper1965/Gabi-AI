"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: agent_routes.py                                                       │
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

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Header,
    Query,
    File,
    UploadFile,
    Form,
)
from sqlalchemy.orm import Session
from src.config.database import get_db
from typing import List, Dict, Any, Optional, Union
import uuid
from src.core.jwt_middleware import (
    get_jwt_token,
    verify_user_client,
)
from src.schemas.schemas import (
    Agent,
    AgentCreate,
    AgentFolder,
    AgentFolderCreate,
    AgentFolderUpdate,
    ApiKey,
    ApiKeyCreate,
    ApiKeyUpdate,
)
from src.services import agent_service, mcp_server_service, apikey_service
import logging
import json

logger = logging.getLogger(__name__)


async def format_agent_tools(
    mcp_servers: List[Dict[str, Any]], db: Session
) -> List[Dict[str, Any]]:
    """Format MCP server tools for agent card skills"""
    formatted_tools = []

    for server in mcp_servers:
        try:
            # Get the MCP server by ID
            server_id = uuid.UUID(server["id"])
            mcp_server = mcp_server_service.get_mcp_server(db, server_id)

            if not mcp_server:
                logger.warning(f"MCP server not found: {server_id}")
                continue

            # Format each tool
            for tool in mcp_server.tools:
                formatted_tool = {
                    "id": tool["id"],
                    "name": tool["name"],
                    "description": tool["description"],
                    "tags": tool["tags"],
                    "examples": tool["examples"],
                    "inputModes": tool["inputModes"],
                    "outputModes": tool["outputModes"],
                }
                formatted_tools.append(formatted_tool)

        except Exception as e:
            logger.error(
                f"Error formatting tools for MCP server {server.get('id')}: {str(e)}"
            )
            continue

    return formatted_tools


router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)


@router.post("/apikeys", response_model=ApiKey, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key: ApiKeyCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Create a new API key"""
    await verify_user_client(payload, db, key.client_id)

    db_key = apikey_service.create_api_key(
        db, key.client_id, key.name, key.provider, key.key_value
    )

    return db_key


@router.get("/apikeys", response_model=List[ApiKey])
async def read_api_keys(
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    skip: int = 0,
    limit: int = 100,
    sort_by: str = Query(
        "name", description="Field to sort: name, provider, created_at"
    ),
    sort_direction: str = Query("asc", description="Sort direction: asc, desc"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """List API keys for a client"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    keys = apikey_service.get_api_keys_by_client(
        db, x_client_id, skip, limit, sort_by, sort_direction
    )
    return keys


@router.get("/apikeys/{key_id}", response_model=ApiKey)
async def read_api_key(
    key_id: uuid.UUID,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Get details of a specific API key"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    key = apikey_service.get_api_key(db, key_id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found"
        )

    # Verify if the key belongs to the specified client
    if key.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key does not belong to the specified client",
        )

    return key


@router.put("/apikeys/{key_id}", response_model=ApiKey)
async def update_api_key(
    key_id: uuid.UUID,
    key_data: ApiKeyUpdate,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Update an API key"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Verify if the key exists
    key = apikey_service.get_api_key(db, key_id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found"
        )

    # Verify if the key belongs to the specified client
    if key.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key does not belong to the specified client",
        )

    # Update the key
    updated_key = apikey_service.update_api_key(
        db,
        key_id,
        key_data.name,
        key_data.provider,
        key_data.key_value,
        key_data.is_active,
    )
    return updated_key


@router.delete("/apikeys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: uuid.UUID,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Deactivate an API key (soft delete)"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Verify if the key exists
    key = apikey_service.get_api_key(db, key_id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found"
        )

    # Verify if the key belongs to the specified client
    if key.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key does not belong to the specified client",
        )

    # Deactivate the key
    if not apikey_service.delete_api_key(db, key_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found"
        )


# Agent folder routes
@router.post(
    "/folders", response_model=AgentFolder, status_code=status.HTTP_201_CREATED
)
async def create_folder(
    folder: AgentFolderCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Create a new folder to organize agents"""
    # Verify if the user has access to the folder's client
    await verify_user_client(payload, db, folder.client_id)

    return agent_service.create_agent_folder(
        db, folder.client_id, folder.name, folder.description
    )


@router.get("/folders", response_model=List[AgentFolder])
async def read_folders(
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """List agent folders for a client"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    return agent_service.get_agent_folders_by_client(db, x_client_id, skip, limit)


@router.get("/folders/{folder_id}", response_model=AgentFolder)
async def read_folder(
    folder_id: uuid.UUID,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Get details of a specific folder"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    folder = agent_service.get_agent_folder(db, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )

    # Verify if the folder belongs to the specified client
    if folder.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Folder does not belong to the specified client",
        )

    return folder


@router.put("/folders/{folder_id}", response_model=AgentFolder)
async def update_folder(
    folder_id: uuid.UUID,
    folder_data: AgentFolderUpdate,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Update an agent folder"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Verify if the folder exists
    folder = agent_service.get_agent_folder(db, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )

    # Verify if the folder belongs to the specified client
    if folder.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Folder does not belong to the specified client",
        )

    # Update the folder
    updated_folder = agent_service.update_agent_folder(
        db, folder_id, folder_data.name, folder_data.description
    )
    return updated_folder


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: uuid.UUID,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Remove an agent folder"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Verify if the folder exists
    folder = agent_service.get_agent_folder(db, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )

    # Verify if the folder belongs to the specified client
    if folder.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Folder does not belong to the specified client",
        )

    # Delete the folder
    if not agent_service.delete_agent_folder(db, folder_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )


@router.get("/folders/{folder_id}/agents", response_model=List[Agent])
async def read_folder_agents(
    folder_id: uuid.UUID,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """List agents in a specific folder"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Verify if the folder exists
    folder = agent_service.get_agent_folder(db, folder_id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
        )

    # Verify if the folder belongs to the specified client
    if folder.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Folder does not belong to the specified client",
        )

    # List the agents in the folder
    agents = agent_service.get_agents_by_folder(db, folder_id, skip, limit)

    # Add agent card URL when needed
    for agent in agents:
        if not agent.agent_card_url:
            agent.agent_card_url = agent.agent_card_url_property

    return agents


@router.put("/{agent_id}/folder", response_model=Agent)
async def assign_agent_to_folder(
    agent_id: uuid.UUID,
    folder_id: Optional[uuid.UUID] = None,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Assign an agent to a folder or remove from the current folder (if folder_id=None)"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Verify if the agent exists
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Verify if the agent belongs to the specified client
    if agent.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent does not belong to the specified client",
        )

    # If folder_id is provided, verify if the folder exists and belongs to the same client
    if folder_id:
        folder = agent_service.get_agent_folder(db, folder_id)
        if not folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
            )

        if folder.client_id != x_client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Folder does not belong to the specified client",
            )

    # Assign the agent to the folder or remove from the current folder
    updated_agent = agent_service.assign_agent_to_folder(db, agent_id, folder_id)

    if not updated_agent.agent_card_url:
        updated_agent.agent_card_url = updated_agent.agent_card_url_property

    return updated_agent


# Agent routes (after specific routes)
@router.get("/", response_model=List[Agent])
async def read_agents(
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    skip: int = 0,
    limit: int = 100,
    folder_id: Optional[uuid.UUID] = Query(None, description="Filter by folder"),
    sort_by: str = Query("name", description="Field to sort: name, created_at"),
    sort_direction: str = Query("asc", description="Sort direction: asc, desc"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Get agents with optional folder filter and sorting
    agents = agent_service.get_agents_by_client(
        db, x_client_id, skip, limit, True, folder_id, sort_by, sort_direction
    )

    for agent in agents:
        if not agent.agent_card_url:
            agent.agent_card_url = agent.agent_card_url_property

    return agents


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Verify if the user has access to the agent's client
    await verify_user_client(payload, db, agent.client_id)

    db_agent = await agent_service.create_agent(db, agent)

    if not db_agent.agent_card_url:
        db_agent.agent_card_url = db_agent.agent_card_url_property

    return db_agent


@router.get("/{agent_id}", response_model=Agent)
async def read_agent(
    agent_id: uuid.UUID,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    db_agent = agent_service.get_agent(db, agent_id)
    if db_agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Verify if the user has access to the agent's client
    await verify_user_client(payload, db, x_client_id)

    if not db_agent.agent_card_url:
        db_agent.agent_card_url = db_agent.agent_card_url_property

    return db_agent


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: uuid.UUID,
    agent_data: Dict[str, Any],
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Get the current agent
    db_agent = agent_service.get_agent(db, agent_id)
    if db_agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Verify if the user has access to the agent's client
    await verify_user_client(payload, db, db_agent.client_id)

    # If trying to change the client_id, verify permission for the new client as well
    if "client_id" in agent_data and agent_data["client_id"] != str(db_agent.client_id):
        new_client_id = uuid.UUID(agent_data["client_id"])
        await verify_user_client(payload, db, new_client_id)

    updated_agent = await agent_service.update_agent(db, agent_id, agent_data)

    if not updated_agent.agent_card_url:
        updated_agent.agent_card_url = updated_agent.agent_card_url_property

    return updated_agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Get the agent
    db_agent = agent_service.get_agent(db, agent_id)
    if db_agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Verify if the user has access to the agent's client
    await verify_user_client(payload, db, db_agent.client_id)

    if not agent_service.delete_agent(db, agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )


@router.post("/{agent_id}/share", response_model=Dict[str, str])
async def share_agent(
    agent_id: uuid.UUID,
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Returns the agent's API key for sharing"""
    await verify_user_client(payload, db, x_client_id)

    # Verify if the agent exists
    agent = agent_service.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Verify if the agent belongs to the specified client
    if agent.client_id != x_client_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent does not belong to the specified client",
        )

    # Verify if API key exists
    if not agent.config or not agent.config.get("api_key"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This agent does not have an API key",
        )

    return {"api_key": agent.config["api_key"]}


@router.get("/{agent_id}/shared", response_model=Agent)
async def get_shared_agent(
    agent_id: uuid.UUID,
    api_key: str = Header(..., alias="x-api-key"),
    db: Session = Depends(get_db),
):
    """Get agent details using only API key authentication"""
    # Verify if the agent exists
    agent = agent_service.get_agent(db, agent_id)
    if not agent or not agent.config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
        )

    # Verify if the API key matches
    if not agent.config.get("api_key") or agent.config.get("api_key") != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    # Add agent card URL if not present
    if not agent.agent_card_url:
        agent.agent_card_url = agent.agent_card_url_property

    return agent


@router.post("/import", response_model=List[Agent], status_code=status.HTTP_201_CREATED)
async def import_agents(
    file: UploadFile = File(...),
    folder_id: Optional[str] = Form(None),
    x_client_id: uuid.UUID = Header(..., alias="x-client-id"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """Import one or more agents from a JSON file"""
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, x_client_id)

    # Convert folder_id to UUID if provided
    folder_uuid = None
    if folder_id:
        try:
            folder_uuid = uuid.UUID(folder_id)
            # Verify the folder exists and belongs to the client
            folder = agent_service.get_agent_folder(db, folder_uuid)
            if not folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found"
                )
            if folder.client_id != x_client_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Folder does not belong to the specified client",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid folder ID format",
            )

    try:
        # Check file type
        if not file.filename.endswith(".json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JSON files are supported",
            )

        # Read file content
        file_content = await file.read()

        try:
            # Parse JSON content
            agents_data = json.loads(file_content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format"
            )

        # Call the service function to import agents
        imported_agents = await agent_service.import_agents_from_json(
            db, agents_data, x_client_id, folder_uuid
        )

        return imported_agents

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in agent import: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing agents: {str(e)}",
        )
