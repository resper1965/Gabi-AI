"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: admin_routes.py                                                       │
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

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from src.config.database import get_db
from src.core.jwt_middleware import get_jwt_token, verify_admin
from src.schemas.audit import AuditLogResponse, AuditLogFilter
from src.services.audit_service import get_audit_logs, create_audit_log
from src.services.user_service import (
    get_admin_users,
    create_admin_user,
    deactivate_user,
)
from src.schemas.user import UserResponse, AdminUserCreate

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_admin)],
    responses={403: {"description": "Permission denied"}},
)


# Audit routes
@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def read_audit_logs(
    filters: AuditLogFilter = Depends(),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """
    Get audit logs with optional filters

    Args:
        filters: Filters for log search
        db: Database session
        payload: JWT token payload

    Returns:
        List[AuditLogResponse]: List of audit logs
    """
    return get_audit_logs(
        db,
        skip=filters.skip,
        limit=filters.limit,
        user_id=filters.user_id,
        action=filters.action,
        resource_type=filters.resource_type,
        resource_id=filters.resource_id,
        start_date=filters.start_date,
        end_date=filters.end_date,
    )


# Admin routes
@router.get("/users", response_model=List[UserResponse])
async def read_admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """
    List admin users

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        payload: JWT token payload

    Returns:
        List[UserResponse]: List of admin users
    """
    return get_admin_users(db, skip, limit)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_admin_user(
    user_data: AdminUserCreate,
    request: Request,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """
    Create a new admin user

    Args:
        user_data: User data to be created
        request: FastAPI Request object
        db: Database session
        payload: JWT token payload

    Returns:
        UserResponse: Created user data

    Raises:
        HTTPException: If there is an error in creation
    """
    # Get current user ID
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to identify the logged in user",
        )

    # Create admin user
    user, message = create_admin_user(db, user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    # Register action in audit log
    create_audit_log(
        db,
        user_id=uuid.UUID(user_id),
        action="create",
        resource_type="admin_user",
        resource_id=str(user.id),
        details={"email": user.email},
        request=request,
    )

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_admin_user(
    user_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_jwt_token),
):
    """
    Deactivate an admin user (does not delete, only deactivates)

    Args:
        user_id: ID of the user to be deactivated
        request: FastAPI Request object
        db: Database session
        payload: JWT token payload

    Raises:
        HTTPException: If there is an error in deactivation
    """
    # Get current user ID
    current_user_id = payload.get("user_id")
    if not current_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to identify the logged in user",
        )

    # Do not allow deactivating yourself
    if str(user_id) == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to deactivate your own user",
        )

    # Deactivate user
    success, message = deactivate_user(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    # Register action in audit log
    create_audit_log(
        db,
        user_id=uuid.UUID(current_user_id),
        action="deactivate",
        resource_type="admin_user",
        resource_id=str(user_id),
        details=None,
        request=request,
    )
