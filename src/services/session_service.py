"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: session_service.py                                                    │
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

from google.adk.sessions import DatabaseSessionService
from sqlalchemy.orm import Session
from src.models.models import Session as SessionModel
from google.adk.events import Event
from google.adk.sessions import Session as SessionADK
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from src.services.agent_service import get_agents_by_client

import uuid
import logging

logger = logging.getLogger(__name__)


def _session_to_dict(session: SessionModel):
    """Convert Session model to dictionary with created_at field"""
    result = {
        "id": session.id,
        "app_name": session.app_name,
        "user_id": session.user_id,
        "state": session.state,
        "create_time": session.create_time,
        "update_time": session.update_time,
        "created_at": session.create_time,
    }
    return result


def get_sessions_by_client(
    db: Session,
    client_id: uuid.UUID,
) -> List[dict]:
    """Search for sessions of a client with pagination"""
    try:
        agents_by_client = get_agents_by_client(db, client_id)
        sessions = []
        for agent in agents_by_client:
            db_sessions = get_sessions_by_agent(db, agent.id)
            sessions.extend(db_sessions)

        return sessions
    except SQLAlchemyError as e:
        logger.error(f"Error searching for sessions of client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for sessions",
        )


def get_sessions_by_agent(
    db: Session,
    agent_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> List[dict]:
    """Search for sessions of an agent with pagination"""
    try:
        agent_id_str = str(agent_id)
        query = db.query(SessionModel).filter(SessionModel.app_name == agent_id_str)

        db_sessions = query.offset(skip).limit(limit).all()
        # Convert each session to dictionary with created_at field
        return [_session_to_dict(session) for session in db_sessions]
    except SQLAlchemyError as e:
        logger.error(f"Error searching for sessions of agent {agent_id_str}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for sessions",
        )


def get_session_by_id(
    session_service: DatabaseSessionService, session_id: str
) -> Optional[SessionADK]:
    """Search for a session by ID"""
    try:
        if not session_id or "_" not in session_id:
            logger.error(f"Invalid session ID: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID. Expected format: app_name_user_id",
            )

        parts = session_id.split("_", 1)
        if len(parts) != 2:
            logger.error(f"Invalid session ID format: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format. Expected format: app_name_user_id",
            )

        user_id, app_name = parts

        session = session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

        if session is None:
            logger.error(f"Session not found: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}",
            )

        return session
    except Exception as e:
        logger.error(f"Error searching for session {session_id}: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching for session: {str(e)}",
        )


def delete_session(session_service: DatabaseSessionService, session_id: str) -> None:
    """Deletes a session by ID"""
    try:
        session = get_session_by_id(session_service, session_id)
        # If we get here, the session exists (get_session_by_id already validates)

        session_service.delete_session(
            app_name=session.app_name,
            user_id=session.user_id,
            session_id=session_id,
        )
        return None
    except HTTPException:
        # Passes HTTP exceptions from get_session_by_id
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}",
        )


def get_session_events(
    session_service: DatabaseSessionService, session_id: str
) -> List[Event]:
    """Search for the events of a session by ID"""
    try:
        session = get_session_by_id(session_service, session_id)
        # If we get here, the session exists (get_session_by_id already validates)

        if not hasattr(session, "events") or session.events is None:
            return []

        sorted_events = sorted(
            session.events,
            key=lambda event: event.timestamp if hasattr(event, "timestamp") else 0,
        )

        return sorted_events

    except HTTPException:
        # Passes HTTP exceptions from get_session_by_id
        raise
    except Exception as e:
        logger.error(f"Error searching for events of session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching for events of session: {str(e)}",
        )
