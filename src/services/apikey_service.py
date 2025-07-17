"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: apikey_service.py                                                     │
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

from src.models.models import ApiKey
from src.utils.crypto import encrypt_api_key, decrypt_api_key
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
import uuid
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


def create_api_key(
    db: Session, client_id: uuid.UUID, name: str, provider: str, key_value: str
) -> ApiKey:
    """Create a new encrypted API key"""
    try:
        # Encrypt the key before saving
        encrypted = encrypt_api_key(key_value)

        # Create the ApiKey object
        api_key = ApiKey(
            client_id=client_id,
            name=name,
            provider=provider,
            encrypted_key=encrypted,
            is_active=True,
        )

        # Save in the database
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        logger.info(f"API key '{name}' created for client {client_id}")
        return api_key
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating API key: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}",
        )


def get_api_key(db: Session, key_id: uuid.UUID) -> Optional[ApiKey]:
    """Get an API key by ID"""
    try:
        return db.query(ApiKey).filter(ApiKey.id == key_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting API key {key_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting API key",
        )


def get_api_keys_by_client(
    db: Session,
    client_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "name",
    sort_direction: str = "asc",
) -> List[ApiKey]:
    """List the API keys of a client"""
    try:
        query = (
            db.query(ApiKey)
            .filter(ApiKey.client_id == client_id)
            .filter(ApiKey.is_active)
        )

        # Apply sorting
        if sort_by == "name":
            if sort_direction.lower() == "desc":
                query = query.order_by(ApiKey.name.desc())
            else:
                query = query.order_by(ApiKey.name)
        elif sort_by == "provider":
            if sort_direction.lower() == "desc":
                query = query.order_by(ApiKey.provider.desc())
            else:
                query = query.order_by(ApiKey.provider)
        elif sort_by == "created_at":
            if sort_direction.lower() == "desc":
                query = query.order_by(ApiKey.created_at.desc())
            else:
                query = query.order_by(ApiKey.created_at)

        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error listing API keys for client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing API keys",
        )


def get_decrypted_api_key(db: Session, key_id: uuid.UUID) -> Optional[str]:
    """Get the decrypted value of an API key"""
    try:
        key = get_api_key(db, key_id)
        if not key or not key.is_active:
            logger.warning(f"API key {key_id} not found or inactive")
            return None
        return decrypt_api_key(key.encrypted_key)
    except Exception as e:
        logger.error(f"Error decrypting API key {key_id}: {str(e)}")
        return None


def update_api_key(
    db: Session,
    key_id: uuid.UUID,
    name: Optional[str] = None,
    provider: Optional[str] = None,
    key_value: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Optional[ApiKey]:
    """Update an API key"""
    try:
        key = get_api_key(db, key_id)
        if not key:
            return None

        if name is not None:
            key.name = name
        if provider is not None:
            key.provider = provider
        if key_value is not None:
            key.encrypted_key = encrypt_api_key(key_value)
        if is_active is not None:
            key.is_active = is_active

        db.commit()
        db.refresh(key)
        logger.info(f"API key {key_id} updated")
        return key
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating API key {key_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating API key",
        )


def delete_api_key(db: Session, key_id: uuid.UUID) -> bool:
    """Remove an API key (soft delete)"""
    try:
        key = get_api_key(db, key_id)
        if not key:
            return False

        # Soft delete - only marks as inactive
        key.is_active = False
        db.commit()
        logger.info(f"API key {key_id} deactivated")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting API key {key_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting API key",
        )
