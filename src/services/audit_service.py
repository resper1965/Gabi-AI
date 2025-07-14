"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: audit_service.py                                                      │
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
from src.models.models import AuditLog
from datetime import datetime
from fastapi import Request
from typing import Optional, Dict, Any, List
import uuid
import logging

logger = logging.getLogger(__name__)


def create_audit_log(
    db: Session,
    user_id: Optional[uuid.UUID],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> Optional[AuditLog]:
    """
    Create a new audit log

    Args:
        db: Database session
        user_id: User ID that performed the action (or None if anonymous)
        action: Action performed (ex: "create", "update", "delete")
        resource_type: Resource type (ex: "client", "agent", "user")
        resource_id: Resource ID (optional)
        details: Additional details of the action (optional)
        request: FastAPI Request object (optional, to get IP and User-Agent)

    Returns:
        Optional[AuditLog]: Created audit log or None in case of error
    """
    try:
        ip_address = None
        user_agent = None

        if request:
            ip_address = request.client.host if hasattr(request, "client") else None
            user_agent = request.headers.get("user-agent")

        # Convert details to serializable format
        if details:
            # Convert UUIDs to strings
            for key, value in details.items():
                if isinstance(value, uuid.UUID):
                    details[key] = str(value)

        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        logger.info(
            f"Audit log created: {action} in {resource_type}"
            + (f" (ID: {resource_id})" if resource_id else "")
        )

        return audit_log

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating audit log: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating audit log: {str(e)}")
        return None


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[AuditLog]:
    """
    Get audit logs with optional filters

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_id: Filter by user ID
        action: Filter by action
        resource_type: Filter by resource type
        resource_id: Filter by resource ID
        start_date: Start date
        end_date: End date

    Returns:
        List[AuditLog]: List of audit logs
    """
    query = db.query(AuditLog)

    # Apply filters, if provided
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if action:
        query = query.filter(AuditLog.action == action)

    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    if resource_id:
        query = query.filter(AuditLog.resource_id == resource_id)

    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)

    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    # Order by creation date (most recent first)
    query = query.order_by(AuditLog.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    return query.all()
