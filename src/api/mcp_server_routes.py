"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: mcp_server_routes.py                                                  │
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

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from src.config.database import get_db
from typing import List
import uuid
from src.core.jwt_middleware import (
    get_jwt_token,
    verify_admin,
)
from src.schemas.schemas import (
    MCPServer,
    MCPServerCreate,
)
from src.services import (
    mcp_server_service,
)
import logging

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/mcp-servers",
    tags=["mcp-servers"],
    responses={404: {"description": "Not found"}},
)

# Last edited by Arley Peter on 2025-05-17
@router.post("/", response_model=MCPServer, status_code=status.HTTP_201_CREATED)
async def create_mcp_server(
    server: MCPServerCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Only administrators can create MCP servers
    await verify_admin(payload)

    return await run_in_threadpool(mcp_server_service.create_mcp_server, db, server)


@router.get("/", response_model=List[MCPServer])
async def read_mcp_servers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # All authenticated users can list MCP servers
    return mcp_server_service.get_mcp_servers(db, skip, limit)


@router.get("/{server_id}", response_model=MCPServer)
async def read_mcp_server(
    server_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # All authenticated users can view MCP server details
    db_server = mcp_server_service.get_mcp_server(db, server_id)
    if db_server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="MCP server not found"
        )
    return db_server


@router.put("/{server_id}", response_model=MCPServer)
async def update_mcp_server(
    server_id: uuid.UUID,
    server: MCPServerCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Only administrators can update MCP servers
    await verify_admin(payload)

    db_server = mcp_server_service.update_mcp_server(db, server_id, server)
    if db_server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="MCP server not found"
        )
    return db_server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcp_server(
    server_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Only administrators can delete MCP servers
    await verify_admin(payload)

    if not mcp_server_service.delete_mcp_server(db, server_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="MCP server not found"
        )
