"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: client_routes.py                                                      │
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
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from src.config.database import get_db
from typing import List
import uuid
from src.core.jwt_middleware import (
    get_jwt_token,
    verify_user_client,
    verify_admin,
    get_current_user_client_id,
)
from src.schemas.schemas import (
    Client,
    ClientCreate,
)
from src.schemas.user import UserCreate, TokenResponse
from src.services import (
    client_service,
)
from src.services.auth_service import create_access_token
import logging

logger = logging.getLogger(__name__)


class ClientRegistration(BaseModel):
    name: str
    email: EmailStr
    password: str


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=Client, status_code=status.HTTP_201_CREATED)
async def create_user(
    registration: ClientRegistration,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """
    Create a client and a user associated with it

    Args:
        registration: Client and user data to be created
        db: Database session
        payload: JWT token payload

    Returns:
        Client: Created client
    """
    # Only administrators can create clients
    await verify_admin(payload)

    # Create ClientCreate and UserCreate objects from ClientRegistration
    client = ClientCreate(name=registration.name, email=registration.email)
    user = UserCreate(
        email=registration.email, password=registration.password, name=registration.name
    )

    # Create client with user
    client_obj, message = client_service.create_client_with_user(db, client, user)
    if not client_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return client_obj


@router.get("/", response_model=List[Client])
async def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # If admin, can see all clients
    # If regular user, can only see their own client
    client_id = get_current_user_client_id(payload)

    if client_id:
        # Regular user - returns only their own client
        client = client_service.get_client(db, client_id)
        return [client] if client else []
    else:
        # Administrator - returns all clients
        return client_service.get_clients(db, skip, limit)


@router.get("/{client_id}", response_model=Client)
async def read_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, client_id)

    db_client = client_service.get_client(db, client_id)
    if db_client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )
    return db_client


@router.put("/{client_id}", response_model=Client)
async def update_client(
    client_id: uuid.UUID,
    client: ClientCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Verify if the user has access to this client's data
    await verify_user_client(payload, db, client_id)

    db_client = client_service.update_client(db, client_id, client)
    if db_client is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )
    return db_client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    # Only administrators can delete clients
    await verify_admin(payload)

    if not client_service.delete_client(db, client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )


@router.post("/{client_id}/impersonate", response_model=TokenResponse)
async def impersonate_client(
    client_id: uuid.UUID,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """
    Allows an administrator to obtain a token to impersonate a client

    Args:
        client_id: ID of the client to impersonate
        db: Database session
        payload: JWT payload of the administrator

    Returns:
        TokenResponse: Access token for the client

    Raises:
        HTTPException: If the user is not an administrator or the client does not exist
    """
    # Verify if the user is an administrator
    await verify_admin(payload)

    # Search for the client
    client = client_service.get_client(db, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    user = client_service.get_client_user(db, client_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with the client not found",
        )

    access_token = create_access_token(user)

    logger.info(
        f"Administrator {payload.get('sub')} impersonated client {client.name} (ID: {client_id})"
    )

    return {"access_token": access_token, "token_type": "bearer"}
