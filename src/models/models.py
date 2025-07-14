"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: models.py                                                             │
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

import os
from sqlalchemy import (
    Column,
    String,
    UUID,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    CheckConstraint,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from src.config.database import Base
import uuid


class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    client_id = Column(
        UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=True
    )
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expiry = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expiry = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship(
        "Client", backref=backref("user", uselist=False, cascade="all, delete-orphan")
    )


class AgentFolder(Base):
    __tablename__ = "agent_folders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Client", backref="agent_folders")

    agents = relationship("Agent", back_populates="folder")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    role = Column(String, nullable=True)
    goal = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)
    model = Column(String, nullable=True, default="")
    api_key_id = Column(
        UUID(as_uuid=True),
        ForeignKey("api_keys.id", ondelete="SET NULL"),
        nullable=True,
    )
    instruction = Column(Text)
    agent_card_url = Column(String, nullable=True)
    folder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_folders.id", ondelete="SET NULL"),
        nullable=True,
    )
    config = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('llm', 'sequential', 'parallel', 'loop', 'a2a', 'workflow', 'crew_ai', 'task')",
            name="check_agent_type",
        ),
    )

    folder = relationship("AgentFolder", back_populates="agents")

    api_key_ref = relationship("ApiKey", foreign_keys=[api_key_id])

    @property
    def agent_card_url_property(self) -> str:
        """Virtual URL for the agent card"""
        if self.agent_card_url:
            return self.agent_card_url

        return f"{os.getenv('API_URL', '')}/api/v1/a2a/{self.id}/.well-known/agent.json"

    def to_dict(self):
        """Converts the object to a dictionary, converting UUIDs to strings"""
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            if isinstance(value, uuid.UUID):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = self._convert_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    (
                        self._convert_dict(item)
                        if isinstance(item, dict)
                        else str(item) if isinstance(item, uuid.UUID) else item
                    )
                    for item in value
                ]
            else:
                result[key] = value
        result["agent_card_url"] = self.agent_card_url_property
        return result

    def _convert_dict(self, d):
        """Converts UUIDs to a dictionary for strings"""
        result = {}
        for key, value in d.items():
            if isinstance(value, uuid.UUID):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = self._convert_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    (
                        self._convert_dict(item)
                        if isinstance(item, dict)
                        else str(item) if isinstance(item, uuid.UUID) else item
                    )
                    for item in value
                ]
            else:
                result[key] = value
        return result


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    config_type = Column(String, nullable=False, default="studio")
    config_json = Column(JSON, nullable=False, default={})
    environments = Column(JSON, nullable=False, default={})
    tools = Column(JSON, nullable=False, default=[])
    type = Column(String, nullable=False, default="official")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('official', 'community')", name="check_mcp_server_type"
        ),
        CheckConstraint(
            "config_type IN ('studio', 'sse')", name="check_mcp_server_config_type"
        ),
    )


class Tool(Base):
    __tablename__ = "tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    config_json = Column(JSON, nullable=False, default={})
    environments = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = {"extend_existing": True, "info": {"skip_autogenerate": True}}

    id = Column(String, primary_key=True)
    app_name = Column(String)
    user_id = Column(String)
    state = Column(JSON)
    create_time = Column(DateTime(timezone=True))
    update_time = Column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="audit_logs")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    encrypted_key = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    client = relationship("Client", backref="api_keys")
