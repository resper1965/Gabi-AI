"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: auth_service.py                                                       │
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
from src.models.models import User
from src.schemas.user import TokenData
from src.services.user_service import get_user_by_email
from src.utils.security import create_jwt_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from src.config.settings import settings
from src.config.database import get_db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Define OAuth2 authentication scheme with password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Get the current user from the JWT token

    Args:
        token: JWT token
        db: Database session

    Returns:
        User: Current user

    Raises:
        HTTPException: If the token is invalid or the user is not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract token data
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token without email (sub)")
            raise credentials_exception

        # Check if the token has expired
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning(f"Token expired for {email}")
            raise credentials_exception

        TokenData(
            sub=email,
            exp=datetime.fromtimestamp(exp),
            is_admin=payload.get("is_admin", False),
            client_id=payload.get("client_id"),
        )

    except JWTError as e:
        logger.error(f"Error decoding JWT token: {str(e)}")
        raise credentials_exception

    # Search for user in the database
    user = get_user_by_email(db, email=email)
    if user is None:
        logger.warning(f"User not found for email: {email}")
        raise credentials_exception

    if not user.is_active:
        logger.warning(f"Attempt to access inactive user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Check if the current user is active

    Args:
        current_user: Current user

    Returns:
        User: Current user if active

    Raises:
        HTTPException: If the user is not active
    """
    if not current_user.is_active:
        logger.warning(f"Attempt to access inactive user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Check if the current user is an administrator

    Args:
        current_user: Current user

    Returns:
        User: Current user if administrator

    Raises:
        HTTPException: If the user is not an administrator
    """
    if not current_user.is_admin:
        logger.warning(
            f"Attempt to access admin by non-admin user: {current_user.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Restricted to administrators.",
        )
    return current_user


def create_access_token(user: User) -> str:
    """
    Create a JWT access token for the user

    Args:
        user: User for which to create the token

    Returns:
        str: JWT token
    """
    # Data to be included in the token
    token_data = {
        "sub": user.email,
        "user_id": str(user.id),
        "is_admin": user.is_admin,
    }

    # Include client_id only if not administrator and client_id is set
    if not user.is_admin and user.client_id:
        token_data["client_id"] = str(user.client_id)

    # Create token
    return create_jwt_token(token_data)
