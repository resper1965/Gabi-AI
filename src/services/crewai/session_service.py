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

from datetime import datetime
import json
import uuid
import base64
import copy
from typing import Any, Dict, List, Optional, Union, Set

from sqlalchemy import create_engine, Boolean, Text, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import (
    sessionmaker,
    relationship,
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, PickleType, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import TypeDecorator

from pydantic import BaseModel

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DynamicJSON(TypeDecorator):
    """JSON type compatible with ADK that uses JSONB in PostgreSQL and TEXT with JSON
    serialization for other databases."""

    impl = Text  # Default implementation is TEXT

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB)
        else:
            return dialect.type_descriptor(Text)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if dialect.name == "postgresql":
                return value
            else:
                return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if dialect.name == "postgresql":
                return value
            else:
                return json.loads(value)
        return value


class Base(DeclarativeBase):
    """Base class for database tables."""

    pass


class StorageSession(Base):
    """Represents a session stored in the database, compatible with ADK."""

    __tablename__ = "sessions"

    app_name: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )

    state: Mapped[MutableDict[str, Any]] = mapped_column(
        MutableDict.as_mutable(DynamicJSON), default={}
    )

    create_time: Mapped[DateTime] = mapped_column(DateTime(), default=func.now())
    update_time: Mapped[DateTime] = mapped_column(
        DateTime(), default=func.now(), onupdate=func.now()
    )

    storage_events: Mapped[list["StorageEvent"]] = relationship(
        "StorageEvent",
        back_populates="storage_session",
    )

    def __repr__(self):
        return f"<StorageSession(id={self.id}, update_time={self.update_time})>"


class StorageEvent(Base):
    """Represents an event stored in the database, compatible with ADK."""

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    app_name: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, primary_key=True)

    invocation_id: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String)
    branch: Mapped[str] = mapped_column(String, nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime(), default=func.now())
    content: Mapped[dict[str, Any]] = mapped_column(DynamicJSON, nullable=True)
    actions: Mapped[MutableDict[str, Any]] = mapped_column(PickleType)

    long_running_tool_ids_json: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    grounding_metadata: Mapped[dict[str, Any]] = mapped_column(
        DynamicJSON, nullable=True
    )
    partial: Mapped[bool] = mapped_column(Boolean, nullable=True)
    turn_complete: Mapped[bool] = mapped_column(Boolean, nullable=True)
    error_code: Mapped[str] = mapped_column(String, nullable=True)
    error_message: Mapped[str] = mapped_column(String, nullable=True)
    interrupted: Mapped[bool] = mapped_column(Boolean, nullable=True)

    storage_session: Mapped[StorageSession] = relationship(
        "StorageSession",
        back_populates="storage_events",
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["app_name", "user_id", "session_id"],
            ["sessions.app_name", "sessions.user_id", "sessions.id"],
            ondelete="CASCADE",
        ),
    )

    @property
    def long_running_tool_ids(self) -> set[str]:
        return (
            set(json.loads(self.long_running_tool_ids_json))
            if self.long_running_tool_ids_json
            else set()
        )

    @long_running_tool_ids.setter
    def long_running_tool_ids(self, value: set[str]):
        if value is None:
            self.long_running_tool_ids_json = None
        else:
            self.long_running_tool_ids_json = json.dumps(list(value))


class StorageAppState(Base):
    """Represents an application state stored in the database, compatible with ADK."""

    __tablename__ = "app_states"

    app_name: Mapped[str] = mapped_column(String, primary_key=True)
    state: Mapped[MutableDict[str, Any]] = mapped_column(
        MutableDict.as_mutable(DynamicJSON), default={}
    )
    update_time: Mapped[DateTime] = mapped_column(
        DateTime(), default=func.now(), onupdate=func.now()
    )


class StorageUserState(Base):
    """Represents a user state stored in the database, compatible with ADK."""

    __tablename__ = "user_states"

    app_name: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, primary_key=True)
    state: Mapped[MutableDict[str, Any]] = mapped_column(
        MutableDict.as_mutable(DynamicJSON), default={}
    )
    update_time: Mapped[DateTime] = mapped_column(
        DateTime(), default=func.now(), onupdate=func.now()
    )


# Pydantic model classes compatible with ADK
class State:
    """Utility class for states, compatible with ADK."""

    APP_PREFIX = "app:"
    USER_PREFIX = "user:"
    TEMP_PREFIX = "temp:"


class Content(BaseModel):
    """Event content model, compatible with ADK."""

    parts: List[Dict[str, Any]]


class Part(BaseModel):
    """Content part model, compatible with ADK."""

    text: Optional[str] = None


class Event(BaseModel):
    """Event model, compatible with ADK."""

    id: Optional[str] = None
    author: str
    branch: Optional[str] = None
    invocation_id: Optional[str] = None
    content: Optional[Content] = None
    actions: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    long_running_tool_ids: Optional[Set[str]] = None
    grounding_metadata: Optional[Dict[str, Any]] = None
    partial: Optional[bool] = None
    turn_complete: Optional[bool] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    interrupted: Optional[bool] = None


class Session(BaseModel):
    """Session model, compatible with ADK."""

    app_name: str
    user_id: str
    id: str
    state: Dict[str, Any] = {}
    events: List[Event] = []
    last_update_time: float

    class Config:
        arbitrary_types_allowed = True


class CrewSessionService:
    """Service for managing CrewAI agent sessions using ADK tables."""

    def __init__(self, db_url: str):
        """
        Initializes the session service.

        Args:
            db_url: Database connection URL.
        """
        try:
            self.engine = create_engine(db_url)
        except Exception as e:
            raise ValueError(f"Failed to create database engine: {e}")

        # Create all tables
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"CrewSessionService started with database at {db_url}")

    def create_session(
        self, agent_id: str, external_id: str, session_id: Optional[str] = None
    ) -> Session:
        """
        Creates a new session for an agent.

        Args:
            agent_id: Agent ID (used as app_name in ADK)
            external_id: External ID (used as user_id in ADK)
            session_id: Optional session ID

        Returns:
            Session: The created session
        """
        session_id = session_id or str(uuid.uuid4())

        with self.Session() as db_session:
            # Check if app and user states already exist
            storage_app_state = db_session.get(StorageAppState, (agent_id))
            storage_user_state = db_session.get(
                StorageUserState, (agent_id, external_id)
            )

            app_state = storage_app_state.state if storage_app_state else {}
            user_state = storage_user_state.state if storage_user_state else {}

            # Create states if they don't exist
            if not storage_app_state:
                storage_app_state = StorageAppState(app_name=agent_id, state={})
                db_session.add(storage_app_state)

            if not storage_user_state:
                storage_user_state = StorageUserState(
                    app_name=agent_id, user_id=external_id, state={}
                )
                db_session.add(storage_user_state)

            # Create session
            storage_session = StorageSession(
                app_name=agent_id,
                user_id=external_id,
                id=session_id,
                state={},
            )
            db_session.add(storage_session)
            db_session.commit()

            # Get timestamp
            db_session.refresh(storage_session)

            # Merge states for response
            merged_state = _merge_state(app_state, user_state, {})

            # Create Session object for return
            session = Session(
                app_name=agent_id,
                user_id=external_id,
                id=session_id,
                state=merged_state,
                last_update_time=storage_session.update_time.timestamp(),
            )

        logger.info(
            f"Session created: {session_id} for agent {agent_id} and user {external_id}"
        )
        return session

    def get_session(
        self, agent_id: str, external_id: str, session_id: str
    ) -> Optional[Session]:
        """
        Retrieves a session from the database.

        Args:
            agent_id: Agent ID
            external_id: User ID
            session_id: Session ID

        Returns:
            Optional[Session]: The retrieved session or None if not found
        """
        with self.Session() as db_session:
            storage_session = db_session.get(
                StorageSession, (agent_id, external_id, session_id)
            )

            if storage_session is None:
                return None

            # Fetch session events
            storage_events = (
                db_session.query(StorageEvent)
                .filter(StorageEvent.session_id == storage_session.id)
                .filter(StorageEvent.app_name == agent_id)
                .filter(StorageEvent.user_id == external_id)
                .all()
            )

            # Fetch states
            storage_app_state = db_session.get(StorageAppState, (agent_id))
            storage_user_state = db_session.get(
                StorageUserState, (agent_id, external_id)
            )

            app_state = storage_app_state.state if storage_app_state else {}
            user_state = storage_user_state.state if storage_user_state else {}
            session_state = storage_session.state

            # Merge states
            merged_state = _merge_state(app_state, user_state, session_state)

            # Create session
            session = Session(
                app_name=agent_id,
                user_id=external_id,
                id=session_id,
                state=merged_state,
                last_update_time=storage_session.update_time.timestamp(),
            )

            # Add events
            session.events = [
                Event(
                    id=e.id,
                    author=e.author,
                    branch=e.branch,
                    invocation_id=e.invocation_id,
                    content=_decode_content(e.content),
                    actions=e.actions,
                    timestamp=e.timestamp.timestamp(),
                    long_running_tool_ids=e.long_running_tool_ids,
                    grounding_metadata=e.grounding_metadata,
                    partial=e.partial,
                    turn_complete=e.turn_complete,
                    error_code=e.error_code,
                    error_message=e.error_message,
                    interrupted=e.interrupted,
                )
                for e in storage_events
            ]

            return session

    def save_session(self, session: Session) -> None:
        """
        Saves a session to the database.

        Args:
            session: The session to save
        """
        with self.Session() as db_session:
            storage_session = db_session.get(
                StorageSession, (session.app_name, session.user_id, session.id)
            )

            if not storage_session:
                logger.error(f"Session not found: {session.id}")
                return

            # Check states
            storage_app_state = db_session.get(StorageAppState, (session.app_name))
            storage_user_state = db_session.get(
                StorageUserState, (session.app_name, session.user_id)
            )

            # Extract state deltas
            app_state_delta = {}
            user_state_delta = {}
            session_state_delta = {}

            # Apply state deltas
            if storage_app_state and app_state_delta:
                storage_app_state.state.update(app_state_delta)

            if storage_user_state and user_state_delta:
                storage_user_state.state.update(user_state_delta)

            storage_session.state.update(session_state_delta)

            # Save new events
            for event in session.events:
                # Check if event already exists
                existing_event = (
                    (
                        db_session.query(StorageEvent)
                        .filter(StorageEvent.id == event.id)
                        .filter(StorageEvent.app_name == session.app_name)
                        .filter(StorageEvent.user_id == session.user_id)
                        .filter(StorageEvent.session_id == session.id)
                        .first()
                    )
                    if event.id
                    else None
                )

                if existing_event:
                    continue

                # Generate ID for the event if it doesn't exist
                if not event.id:
                    event.id = str(uuid.uuid4())

                # Create timestamp if it doesn't exist
                if not event.timestamp:
                    event.timestamp = datetime.now().timestamp()

                # Create StorageEvent object
                storage_event = StorageEvent(
                    id=event.id,
                    app_name=session.app_name,
                    user_id=session.user_id,
                    session_id=session.id,
                    invocation_id=event.invocation_id or str(uuid.uuid4()),
                    author=event.author,
                    branch=event.branch,
                    timestamp=datetime.fromtimestamp(event.timestamp),
                    actions=event.actions or {},
                    long_running_tool_ids=event.long_running_tool_ids or set(),
                    grounding_metadata=event.grounding_metadata,
                    partial=event.partial,
                    turn_complete=event.turn_complete,
                    error_code=event.error_code,
                    error_message=event.error_message,
                    interrupted=event.interrupted,
                )

                # Encode content, if it exists
                if event.content:
                    encoded_content = event.content.model_dump(exclude_none=True)
                    # Solution for serialization issues with multimedia content
                    for p in encoded_content.get("parts", []):
                        if "inline_data" in p:
                            p["inline_data"]["data"] = (
                                base64.b64encode(p["inline_data"]["data"]).decode(
                                    "utf-8"
                                ),
                            )
                    storage_event.content = encoded_content

                db_session.add(storage_event)

            # Commit changes
            db_session.commit()

            # Update timestamp in session
            db_session.refresh(storage_session)
            session.last_update_time = storage_session.update_time.timestamp()

        logger.info(f"Session saved: {session.id} with {len(session.events)} events")

    def list_sessions(self, agent_id: str, external_id: str) -> List[Dict[str, Any]]:
        """
        Lists all sessions for an agent and user.

        Args:
            agent_id: Agent ID
            external_id: User ID

        Returns:
            List[Dict[str, Any]]: List of summarized sessions
        """
        with self.Session() as db_session:
            sessions = (
                db_session.query(StorageSession)
                .filter(StorageSession.app_name == agent_id)
                .filter(StorageSession.user_id == external_id)
                .all()
            )

            result = []
            for session in sessions:
                result.append(
                    {
                        "app_name": session.app_name,
                        "user_id": session.user_id,
                        "id": session.id,
                        "created_at": session.create_time.isoformat(),
                        "updated_at": session.update_time.isoformat(),
                    }
                )

            return result

    def delete_session(self, agent_id: str, external_id: str, session_id: str) -> bool:
        """
        Deletes a session from the database.

        Args:
            agent_id: Agent ID
            external_id: User ID
            session_id: Session ID

        Returns:
            bool: True if the session was deleted, False otherwise
        """
        from sqlalchemy import delete

        with self.Session() as db_session:
            stmt = delete(StorageSession).where(
                StorageSession.app_name == agent_id,
                StorageSession.user_id == external_id,
                StorageSession.id == session_id,
            )
            result = db_session.execute(stmt)
            db_session.commit()

            logger.info(f"Session deleted: {session_id}")
            return result.rowcount > 0


# Utility functions compatible with ADK


def _extract_state_delta(state: dict[str, Any]):
    """Extracts state deltas between app, user, and session."""
    app_state_delta = {}
    user_state_delta = {}
    session_state_delta = {}

    if state:
        for key in state.keys():
            if key.startswith(State.APP_PREFIX):
                app_state_delta[key.removeprefix(State.APP_PREFIX)] = state[key]
            elif key.startswith(State.USER_PREFIX):
                user_state_delta[key.removeprefix(State.USER_PREFIX)] = state[key]
            elif not key.startswith(State.TEMP_PREFIX):
                session_state_delta[key] = state[key]

    return app_state_delta, user_state_delta, session_state_delta


def _merge_state(app_state, user_state, session_state):
    """Merges app, user, and session states into a single object."""
    merged_state = copy.deepcopy(session_state)

    for key in app_state.keys():
        merged_state[State.APP_PREFIX + key] = app_state[key]

    for key in user_state.keys():
        merged_state[State.USER_PREFIX + key] = user_state[key]

    return merged_state


def _decode_content(content: Optional[dict[str, Any]]) -> Optional[Content]:
    """Decodes event content potentially with binary data."""
    if not content:
        return None

    for p in content.get("parts", []):
        if "inline_data" in p and isinstance(p["inline_data"].get("data"), tuple):
            p["inline_data"]["data"] = base64.b64decode(p["inline_data"]["data"][0])

    return Content.model_validate(content)
