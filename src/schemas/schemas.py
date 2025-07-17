"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: schemas.py                                                            │
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

from pydantic import BaseModel, Field, validator, UUID4, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import uuid
import re
from src.schemas.agent_config import LLMConfig, AgentConfig


class ClientBase(BaseModel):
    name: str
    email: Optional[str] = None

    @validator("email")
    def validate_email(cls, v):
        if v is None:
            return v
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyBase(BaseModel):
    name: str
    provider: str


class ApiKeyCreate(ApiKeyBase):
    client_id: UUID4
    key_value: str


class ApiKeyUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    key_value: Optional[str] = None
    is_active: Optional[bool] = None


class ApiKey(ApiKeyBase):
    id: UUID4
    client_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AgentBase(BaseModel):
    name: Optional[str] = Field(
        None, description="Agent name (no spaces or special characters)"
    )
    description: Optional[str] = Field(None, description="Agent description")
    role: Optional[str] = Field(None, description="Agent role in the system")
    goal: Optional[str] = Field(None, description="Agent goal or objective")
    type: str = Field(
        ...,
        description="Agent type (llm, sequential, parallel, loop, a2a, workflow, task)",
    )
    model: Optional[str] = Field(
        None, description="Agent model (required only for llm type)"
    )
    api_key_id: Optional[UUID4] = Field(
        None, description="Reference to a stored API Key ID"
    )
    instruction: Optional[str] = None
    agent_card_url: Optional[str] = Field(
        None, description="Agent card URL (required for a2a type)"
    )
    folder_id: Optional[UUID4] = Field(
        None, description="ID of the folder this agent belongs to"
    )
    config: Any = Field(None, description="Agent configuration based on type")

    @validator("name")
    def validate_name(cls, v, values):
        if values.get("type") == "a2a":
            return v

        if not v:
            raise ValueError("Name is required for non-a2a agent types")

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Agent name cannot contain spaces or special characters")
        return v

    @validator("type")
    def validate_type(cls, v):
        if v not in [
            "llm",
            "sequential",
            "parallel",
            "loop",
            "a2a",
            "workflow",
            "task",
        ]:
            raise ValueError(
                "Invalid agent type. Must be: llm, sequential, parallel, loop, a2a, workflow or task"
            )
        return v

    @validator("agent_card_url")
    def validate_agent_card_url(cls, v, values):
        if "type" in values and values["type"] == "a2a":
            if not v:
                raise ValueError("agent_card_url is required for a2a type agents")
            if not v.endswith("/.well-known/agent.json"):
                raise ValueError("agent_card_url must end with /.well-known/agent.json")
        return v

    @validator("model")
    def validate_model(cls, v, values):
        if "type" in values and values["type"] == "llm" and not v:
            raise ValueError("Model is required for llm type agents")
        return v

    @validator("api_key_id")
    def validate_api_key_id(cls, v, values):
        return v

    @validator("config")
    def validate_config(cls, v, values):
        if "type" in values and values["type"] == "a2a":
            return v or {}

        if "type" not in values:
            return v

        # For workflow agents, we do not perform any validation
        if "type" in values and values["type"] == "workflow":
            return v

        if not v and values.get("type") != "a2a":
            raise ValueError(
                f"Configuration is required for {values.get('type')} agent type"
            )

        if values["type"] == "llm":
            if isinstance(v, dict):
                try:
                    # Convert the dictionary to LLMConfig
                    v = LLMConfig(**v)
                except Exception as e:
                    raise ValueError(f"Invalid LLM configuration for agent: {str(e)}")
            elif not isinstance(v, LLMConfig):
                raise ValueError("Invalid LLM configuration for agent")
        elif values["type"] in ["sequential", "parallel", "loop"]:
            if not isinstance(v, dict):
                raise ValueError(f'Invalid configuration for agent {values["type"]}')
            if "sub_agents" not in v:
                raise ValueError(f'Agent {values["type"]} must have sub_agents')
            if not isinstance(v["sub_agents"], list):
                raise ValueError("sub_agents must be a list")
            if not v["sub_agents"]:
                raise ValueError(
                    f'Agent {values["type"]} must have at least one sub-agent'
                )
        elif values["type"] == "task":
            if not isinstance(v, dict):
                raise ValueError(f'Invalid configuration for agent {values["type"]}')
            if "tasks" not in v:
                raise ValueError(f'Agent {values["type"]} must have tasks')
            if not isinstance(v["tasks"], list):
                raise ValueError("tasks must be a list")
            if not v["tasks"]:
                raise ValueError(f'Agent {values["type"]} must have at least one task')
            for task in v["tasks"]:
                if not isinstance(task, dict):
                    raise ValueError("Each task must be a dictionary")
                required_fields = ["agent_id", "description", "expected_output"]
                for field in required_fields:
                    if field not in task:
                        raise ValueError(f"Task missing required field: {field}")

            if "sub_agents" in v and v["sub_agents"] is not None:
                if not isinstance(v["sub_agents"], list):
                    raise ValueError("sub_agents must be a list")

            return v

        return v


class AgentCreate(AgentBase):
    client_id: UUID


class Agent(AgentBase):
    id: UUID
    client_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    agent_card_url: Optional[str] = None
    folder_id: Optional[UUID4] = None

    class Config:
        from_attributes = True

    @validator("agent_card_url", pre=True)
    def set_agent_card_url(cls, v, values):
        if v:
            return v

        if "id" in values:
            from os import getenv

            return f"{getenv('API_URL', '')}/api/v1/a2a/{values['id']}/.well-known/agent.json"

        return v


class ToolConfig(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    inputModes: List[str] = Field(default_factory=list)
    outputModes: List[str] = Field(default_factory=list)

# Last edited by Arley Peter on 2025-05-17
class MCPServerBase(BaseModel):
    name: str
    description: Optional[str] = None
    config_type: str = Field(default="studio")
    config_json: Dict[str, Any] = Field(default_factory=dict)
    environments: Dict[str, Any] = Field(default_factory=dict)
    tools: Optional[List[ToolConfig]] = Field(default_factory=list) 
    type: str = Field(default="official")


class MCPServerCreate(MCPServerBase):
    pass


class MCPServer(MCPServerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    config_json: Dict[str, Any] = Field(default_factory=dict)
    environments: Dict[str, Any] = Field(default_factory=dict)


class ToolCreate(ToolBase):
    pass


class Tool(ToolBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentFolderBase(BaseModel):
    name: str
    description: Optional[str] = None


class AgentFolderCreate(AgentFolderBase):
    client_id: UUID4


class AgentFolderUpdate(AgentFolderBase):
    pass


class AgentFolder(AgentFolderBase):
    id: UUID4
    client_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
