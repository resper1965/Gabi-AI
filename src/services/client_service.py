"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: client_service.p                                                      │
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
from src.models.models import Client, User
from src.schemas.schemas import ClientCreate
from src.schemas.user import UserCreate
from src.services.user_service import create_user
from typing import List, Optional, Tuple
import uuid
import logging

logger = logging.getLogger(__name__)


def get_client(db: Session, client_id: uuid.UUID) -> Optional[Client]:
    """Search for a client by ID"""
    try:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            logger.warning(f"Client not found: {client_id}")
            return None
        return client
    except SQLAlchemyError as e:
        logger.error(f"Error searching for client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for client",
        )


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
    """Search for all clients with pagination"""
    try:
        return db.query(Client).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error searching for clients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for clients",
        )


def create_client(db: Session, client: ClientCreate) -> Client:
    """Create a new client"""
    try:
        db_client = Client(**client.model_dump())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        logger.info(f"Client created successfully: {db_client.id}")
        return db_client
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating client",
        )


def update_client(
    db: Session, client_id: uuid.UUID, client: ClientCreate
) -> Optional[Client]:
    """Updates an existing client"""
    try:
        db_client = get_client(db, client_id)
        if not db_client:
            return None

        for key, value in client.model_dump().items():
            setattr(db_client, key, value)

        db.commit()
        db.refresh(db_client)
        logger.info(f"Client updated successfully: {client_id}")
        return db_client
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating client",
        )


def delete_client(db: Session, client_id: uuid.UUID) -> bool:
    """Removes a client"""
    try:
        db_client = get_client(db, client_id)
        if not db_client:
            return False

        db.delete(db_client)
        db.commit()
        logger.info(f"Client removed successfully: {client_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error removing client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing client",
        )


def create_client_with_user(
    db: Session, client_data: ClientCreate, user_data: UserCreate
) -> Tuple[Optional[Client], str]:
    """
    Creates a new client with an associated user

    Args:
        db: Database session
        client_data: Client data to be created
        user_data: User data to be created

    Returns:
        Tuple[Optional[Client], str]: Tuple with the created client (or None in case of error) and status message
    """
    try:
        # Start transaction - first create the client
        client = Client(**client_data.model_dump())
        db.add(client)
        db.flush()  # Get client ID without committing the transaction

        # Use client ID to create the associated user
        user, message = create_user(
            db, user_data, is_admin=False, client_id=client.id, auto_verify=False
        )

        if not user:
            # If there was an error creating the user, rollback
            db.rollback()
            logger.error(f"Error creating user for client: {message}")
            return None, f"Error creating user: {message}"

        # If everything went well, commit the transaction
        db.commit()
        logger.info(f"Client and user created successfully: {client.id}")
        return client, "Client and user created successfully"

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating client with user: {str(e)}")
        return None, f"Error creating client with user: {str(e)}"

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating client with user: {str(e)}")
        return None, f"Unexpected error: {str(e)}"


def get_client_user(db: Session, client_id: uuid.UUID) -> Optional[User]:
    """
    Search for the user associated with a client

    Args:
        db: Database session
        client_id: ID of the client

    Returns:
        Optional[User]: User associated with the client or None
    """
    try:
        user = db.query(User).filter(User.client_id == client_id).first()
        if not user:
            logger.warning(f"User not found for client: {client_id}")
            return None
        return user
    except SQLAlchemyError as e:
        logger.error(f"Error searching for user for client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for user for client",
        )
