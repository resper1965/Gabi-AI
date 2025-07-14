"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: main.py                                                               │
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
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.config.database import engine, Base
from src.config.settings import settings
from src.utils.logger import setup_logger
from src.utils.otel import init_otel

# Necessary for other modules
from src.services.service_providers import session_service  # noqa: F401
from src.services.service_providers import artifacts_service  # noqa: F401
from src.services.service_providers import memory_service  # noqa: F401

import src.api.auth_routes
import src.api.admin_routes
import src.api.chat_routes
import src.api.session_routes
import src.api.agent_routes
import src.api.mcp_server_routes
import src.api.tool_routes
import src.api.client_routes
import src.api.a2a_routes

# Add the root directory to PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Configure logger
logger = setup_logger(__name__)

# FastAPI initialization
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    redirect_slashes=False,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files configuration
static_dir = Path("static")
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# PostgreSQL configuration
POSTGRES_CONNECTION_STRING = os.getenv(
    "POSTGRES_CONNECTION_STRING", "postgresql://postgres:root@localhost:5432/evo_ai"
)

# Create database tables
Base.metadata.create_all(bind=engine)

API_PREFIX = "/api/v1"

# Define router references
auth_router = src.api.auth_routes.router
admin_router = src.api.admin_routes.router
chat_router = src.api.chat_routes.router
session_router = src.api.session_routes.router
agent_router = src.api.agent_routes.router
mcp_server_router = src.api.mcp_server_routes.router
tool_router = src.api.tool_routes.router
client_router = src.api.client_routes.router
a2a_router = src.api.a2a_routes.router

# Include routes
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(mcp_server_router, prefix=API_PREFIX)
app.include_router(tool_router, prefix=API_PREFIX)
app.include_router(client_router, prefix=API_PREFIX)
app.include_router(chat_router, prefix=API_PREFIX)
app.include_router(session_router, prefix=API_PREFIX)
app.include_router(agent_router, prefix=API_PREFIX)
app.include_router(a2a_router, prefix=API_PREFIX)

# Inicializa o OpenTelemetry para Langfuse
init_otel()


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Evo AI API",
        "documentation": "/docs",
        "version": settings.API_VERSION,
        "auth": "To access the API, use JWT authentication via '/api/v1/auth/login'",
    }
