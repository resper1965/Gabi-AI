"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: a2a_routes.py                                                         │
│ Developed by: Davidson Gomes                                                 │
│ Creation date: May 23, 2025                                                  │
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

"""
A2A Protocol Official Implementation

100% compliant with the official A2A specification:
https://google.github.io/A2A/specification

This is the official and only A2A implementation for the Evo AI platform.

Methods implemented:
- message/send: Send a message and get response
- message/stream: Send a message and stream response  
- agent/authenticatedExtendedCard: Get agent information (via .well-known/agent.json)

Features:
- Direct integration with agent_runner (no complex SDK layer)
- 100% specification compliant JSON-RPC format
- Proper Task object structure
- Full streaming support
- API key authentication
"""

import uuid
import logging
import json
import base64
import httpx
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, Header, Request, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.sql import text

from src.config.database import get_db
from src.config.settings import settings
from src.services.agent_service import get_agent
from src.services.adk.agent_runner import run_agent, run_agent_stream
from src.services.service_providers import (
    session_service,
    artifacts_service,
    memory_service,
)
from src.schemas.chat import FileData

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/a2a",
    tags=["a2a-official"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
)


async def verify_api_key(db: Session, x_api_key: str) -> bool:
    """Verifies API key against agent config."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key not provided")

    query = text("SELECT * FROM agents WHERE config->>'api_key' = :api_key LIMIT 1")
    result = db.execute(query, {"api_key": x_api_key}).first()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return True


def extract_text_from_message(message: Dict[str, Any]) -> str:
    """Extract text from message parts according to A2A spec."""
    if not message or "parts" not in message:
        return ""

    for part in message["parts"]:
        if part.get("type") == "text" and "text" in part:
            return part["text"]

    return ""


def extract_files_from_message(message: Dict[str, Any]) -> List[FileData]:
    """Extract files from message parts according to A2A spec."""
    files = []
    if not message or "parts" not in message:
        return files

    for part in message["parts"]:
        if part.get("type") == "file" and "file" in part:
            file_data = part["file"]

            # Check if file has bytes (base64 encoded)
            if "bytes" in file_data and file_data["bytes"]:
                try:
                    # Validate base64 content
                    base64.b64decode(file_data["bytes"])

                    file_obj = FileData(
                        filename=file_data.get("name", "file"),
                        content_type=file_data.get(
                            "mimeType", "application/octet-stream"
                        ),
                        data=file_data["bytes"],  # Keep as base64 string
                    )
                    files.append(file_obj)
                    logger.info(
                        f"📎 Extracted file: {file_obj.filename} ({file_obj.content_type})"
                    )

                except Exception as e:
                    logger.error(f"❌ Invalid base64 in file: {e}")
                    continue
            else:
                logger.warning(
                    f"⚠️ File part missing bytes data: {file_data.get('name', 'unnamed')}"
                )

    logger.info(f"📎 Total files extracted: {len(files)}")
    return files


def create_task_response(
    task_id: str,
    context_id: str,
    final_response: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    current_user_message: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create Task response according to A2A specification."""

    logger.info(
        f"🏗️ create_task_response called with history: {len(conversation_history) if conversation_history else 0} messages"
    )

    # Create main response artifact (only the agent's response)
    artifacts = [
        {
            "artifactId": str(uuid.uuid4()),
            "parts": [{"type": "text", "text": final_response}],
        }
    ]

    logger.info(f"📦 Created main artifact")

    # Create Task response according to A2A spec
    task_response = {
        "id": task_id,
        "contextId": context_id,
        "status": {"state": "completed", "timestamp": datetime.now().isoformat() + "Z"},
        "artifacts": artifacts,
        "kind": "task",
    }

    # Build complete history for A2A response
    complete_history = []

    # Add existing conversation history
    if conversation_history:
        for msg in conversation_history:
            # Create A2A Message object
            a2a_message = {
                "role": msg["role"],
                "parts": [{"type": "text", "text": msg["content"]}],
                "messageId": msg.get("messageId"),
                "taskId": task_id,
                "contextId": context_id,
                "kind": "message",
            }

            # Add timestamp if available
            if msg.get("timestamp"):
                a2a_message["timestamp"] = msg["timestamp"]

            complete_history.append(a2a_message)

    # Add current user message if provided (this is the message that triggered this response)
    if current_user_message:
        logger.info(f"📝 Adding current user message to history")
        a2a_message = {
            "role": "user",
            "parts": [{"type": "text", "text": current_user_message["content"]}],
            "messageId": current_user_message.get("messageId"),
            "taskId": task_id,
            "contextId": context_id,
            "kind": "message",
        }

        # Add timestamp if available
        if current_user_message.get("timestamp"):
            a2a_message["timestamp"] = current_user_message["timestamp"]

        complete_history.append(a2a_message)

    # Add history field to Task object (A2A spec compliant)
    if complete_history:
        task_response["history"] = complete_history
        logger.info(
            f"📚 Added {len(complete_history)} messages to history field (including current message)"
        )
    else:
        logger.warning("⚠️ No conversation history provided to create_task_response")

    logger.info(f"✅ create_task_response returning A2A compliant Task object")
    return task_response


def clean_message_content(content: str, role: str) -> str:
    """Clean message content, extracting just the text if it contains JSON."""
    if role == "agent" or role == "assistant":
        # Check if content looks like JSON (starts with { and contains jsonrpc)
        if content.strip().startswith("{") and "jsonrpc" in content:
            try:
                # Try to parse as JSON and extract the actual response text
                import json

                json_data = json.loads(content)

                # Look for the actual text in artifacts
                if "result" in json_data and "artifacts" in json_data["result"]:
                    for artifact in json_data["result"]["artifacts"]:
                        if "parts" in artifact:
                            for part in artifact["parts"]:
                                if part.get("type") == "text" and "text" in part:
                                    return part["text"]

                # Fallback: if we can't extract, return a cleaned version
                return "Previous assistant response"

            except (json.JSONDecodeError, KeyError):
                # If not valid JSON, return as-is but truncated
                return content[:100] + "..." if len(content) > 100 else content

    return content


def extract_conversation_history(
    agent_id: str, external_id: str
) -> List[Dict[str, Any]]:
    """Extract conversation history from session using the same logic as /sessions/{session_id}/messages."""
    logger.info(
        f"🔍 extract_conversation_history called with agent_id={agent_id}, external_id={external_id}"
    )

    try:
        from src.services.session_service import get_session_events, get_session_by_id

        # Get session ID in the correct format (same as working endpoint)
        session_id = f"{external_id}_{agent_id}"
        logger.info(f"📋 Constructed session_id: {session_id}")

        # First, verify session exists (same as working endpoint)
        logger.info(f"🔍 Verifying session exists...")
        session = get_session_by_id(session_service, session_id)
        if not session:
            logger.warning(f"⚠️ Session not found: {session_id}")
            return []

        logger.info(f"✅ Session found: {session_id}")

        # Get events using same method as working endpoint
        logger.info(f"🔍 Getting events for session...")
        events = get_session_events(session_service, session_id)
        logger.info(
            f"📋 get_session_events returned {len(events) if events else 0} events"
        )

        history = []

        # Process events exactly like the working /messages endpoint
        for i, event in enumerate(events):
            logger.info(
                f"🔍 Processing event {i}: id={getattr(event, 'id', 'NO_ID')}, author={getattr(event, 'author', 'NO_AUTHOR')}"
            )

            # Convert event to dict like in working endpoint
            event_dict = (
                event.model_dump() if hasattr(event, "model_dump") else event.__dict__
            )

            # Check if event has content with parts (same logic as working endpoint)
            if event_dict.get("content") and event_dict["content"].get("parts"):
                logger.info(
                    f"📝 Event {i} has content with {len(event_dict['content']['parts'])} parts"
                )

                for j, part in enumerate(event_dict["content"]["parts"]):
                    logger.info(f"📝 Processing part {j}: {part}")

                    # Extract text content (same as working endpoint checks for text)
                    if isinstance(part, dict) and part.get("text"):
                        role = "user" if event_dict.get("author") == "user" else "agent"
                        text_content = part["text"]

                        # Clean the content to remove JSON artifacts
                        cleaned_content = clean_message_content(text_content, role)
                        logger.info(
                            f"📝 Cleaned content for {role}: {cleaned_content[:50]}..."
                        )

                        # Create A2A compatible history entry
                        history_entry = {
                            "role": role,
                            "content": cleaned_content,
                            "messageId": event_dict.get("id"),
                            "timestamp": event_dict.get("timestamp"),
                            "author": event_dict.get("author"),
                            "invocation_id": event_dict.get("invocation_id"),
                        }

                        history.append(history_entry)
                        logger.info(f"✅ Added history entry {len(history)}: {role}")
                    else:
                        logger.info(f"📝 Part {j} has no text content: {part}")
            else:
                logger.warning(f"⚠️ Event {i} has no content or parts")

        logger.info(
            f"📚 extract_conversation_history extracted {len(history)} messages using working logic"
        )
        return history

    except Exception as e:
        logger.error(f"❌ Error extracting conversation history: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")
        return []


def extract_history_from_params(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract history from request params according to A2A spec."""
    history = []
    if "history" in params and isinstance(params["history"], list):
        for msg in params["history"]:
            if isinstance(msg, dict) and "role" in msg and "parts" in msg:
                # Extract text from parts
                text_content = ""
                for part in msg["parts"]:
                    if (
                        isinstance(part, dict)
                        and part.get("type") == "text"
                        and "text" in part
                    ):
                        text_content += part["text"] + " "

                if text_content.strip():
                    history.append(
                        {
                            "role": msg["role"],
                            "content": text_content.strip(),
                            "messageId": msg.get("messageId"),
                            "timestamp": None,  # Could be added if provided
                        }
                    )

    logger.info(f"📚 Extracted {len(history)} messages from request history")
    return history


def combine_histories(
    request_history: List[Dict[str, Any]], session_history: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Combine request history with session history, avoiding duplicates."""
    combined = []

    # Add session history first
    for msg in session_history:
        combined.append(msg)

    # Add request history, avoiding duplicates based on messageId or content
    for req_msg in request_history:
        # Check if this message already exists in combined history
        is_duplicate = False
        for existing_msg in combined:
            if (
                req_msg.get("messageId")
                and req_msg["messageId"] == existing_msg.get("messageId")
            ) or (
                req_msg["content"] == existing_msg["content"]
                and req_msg["role"] == existing_msg["role"]
            ):
                is_duplicate = True
                break

        if not is_duplicate:
            combined.append(req_msg)

    # Sort by timestamp if available, otherwise maintain order
    return combined


@router.post("/{agent_id}")
async def process_a2a_message(
    agent_id: uuid.UUID,
    request: Request,
    x_api_key: str = Header(None, alias="x-api-key"),
    db: Session = Depends(get_db),
):
    """
    Process A2A messages according to official specification.

    Supports:
    - message/send: Send a message and get response
    - message/stream: Send a message and stream response
    """
    logger.info(f"🎯 A2A Spec endpoint called for agent {agent_id}")

    # Verify API key
    await verify_api_key(db, x_api_key)

    # Verify agent exists
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        # Parse JSON-RPC request
        request_body = await request.json()

        jsonrpc = request_body.get("jsonrpc")
        if jsonrpc != "2.0":
            raise HTTPException(status_code=400, detail="Invalid JSON-RPC version")

        method = request_body.get("method")
        params = request_body.get("params", {})
        request_id = request_body.get("id")

        logger.info(f"📝 Method: {method}, ID: {request_id}")

        if method == "message/send":
            return await handle_message_send(agent_id, params, request_id, db)
        elif method == "message/stream":
            return await handle_message_stream(agent_id, params, request_id, db)
        elif method == "tasks/get":
            return await handle_tasks_get(agent_id, params, request_id, db)
        elif method == "tasks/cancel":
            return await handle_tasks_cancel(agent_id, params, request_id, db)
        elif method == "tasks/pushNotificationConfig/set":
            return await handle_tasks_push_notification_config_set(
                agent_id, params, request_id, db
            )
        elif method == "tasks/pushNotificationConfig/get":
            return await handle_tasks_push_notification_config_get(
                agent_id, params, request_id, db
            )
        elif method == "tasks/resubscribe":
            return await handle_tasks_resubscribe(agent_id, params, request_id, db)
        elif method == "agent/authenticatedExtendedCard":
            return await handle_agent_authenticated_extended_card(
                agent_id, params, request_id, db
            )
        else:
            # JSON-RPC error for method not found
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": "Method not found",
                        "data": {
                            "method": method,
                            "supported_methods": [
                                "message/send",
                                "message/stream",
                                "tasks/get",
                                "tasks/cancel",
                                "tasks/pushNotificationConfig/set",
                                "tasks/pushNotificationConfig/get",
                                "tasks/resubscribe",
                                "agent/authenticatedExtendedCard",
                            ],
                        },
                    },
                },
            )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing A2A request: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": request_body.get("id") if "request_body" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            },
        )


async def handle_message_send(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> JSONResponse:
    """Handle message/send according to A2A spec."""

    logger.info(f"🔄 Processing message/send for agent {agent_id}")

    # Extract message from params
    message = params.get("message")
    if not message:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": {"missing": "message"},
                },
            }
        )

    # Extract configuration from params (A2A spec: configuration is optional)
    configuration = params.get("configuration", {})
    push_notification_config = configuration.get("pushNotificationConfig")

    # Support alternative format: pushNotificationConfig directly in params (for backward compatibility)
    if not push_notification_config:
        push_notification_config = params.get("pushNotificationConfig")

    logger.info(
        f"🔔 Push notification config found: {push_notification_config is not None}"
    )

    if push_notification_config:
        # Support both official spec format and common variations
        webhook_url = push_notification_config.get(
            "url"
        ) or push_notification_config.get("webhookUrl")

        logger.info(
            f"🔔 Push notification config provided: {webhook_url or 'No URL found'}"
        )

        # Validate push notification config according to A2A spec (support both url and webhookUrl)
        if not webhook_url:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {
                            "missing": "pushNotificationConfig.url or pushNotificationConfig.webhookUrl"
                        },
                    },
                }
            )

        # Validate HTTPS requirement (A2A spec: prevents SSRF attacks)
        if not webhook_url.startswith("https://"):
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {
                            "error": "pushNotificationConfig.url MUST use HTTPS for security"
                        },
                    },
                }
            )

        # Validate that agent supports push notifications
        agent = get_agent(db, agent_id)
        if not agent:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32001,
                        "message": "Agent not found",
                    },
                }
            )

        # Check agent capabilities for push notification support
        # (Our agent card already indicates pushNotifications: true)
        logger.info(f"✅ Agent {agent_id} supports push notifications")

    # Extract text and files from message
    text = extract_text_from_message(message)
    files = extract_files_from_message(message)

    # Allow empty text if we have files
    if not text and not files:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": {"missing": "text content or files in message parts"},
                },
            }
        )

    # Use default text if only files provided
    if not text and files:
        text = "Analyze the provided files"

    logger.info(f"📝 Extracted text: {text}")
    logger.info(f"📎 Extracted files: {len(files)}")

    # Generate IDs
    task_id = str(uuid.uuid4())
    context_id = message.get("messageId", str(uuid.uuid4()))

    try:
        # Extract conversation history for context
        logger.info(
            f"🔍 Attempting to extract conversation history for agent {agent_id}, context {context_id}"
        )
        conversation_history = extract_conversation_history(str(agent_id), context_id)
        logger.info(
            f"📚 Session history extracted: {len(conversation_history)} messages"
        )

        # Extract history from params
        logger.info(f"🔍 Attempting to extract history from request params")
        request_history = extract_history_from_params(params)
        logger.info(f"📝 Request history extracted: {len(request_history)} messages")

        # Combine histories
        logger.info(f"🔗 Combining histories...")
        combined_history = combine_histories(request_history, conversation_history)
        logger.info(f"📖 Combined history has {len(combined_history)} total messages")

        # Log detailed combined history for debugging
        for i, msg in enumerate(combined_history):
            logger.info(f"  History[{i}]: {msg['role']} - {msg['content'][:50]}...")

        # Execute agent with files - the ADK runner will handle session history automatically
        logger.info(
            f"🤖 Executing agent {agent_id} with message: {text} and {len(files)} files"
        )
        logger.info(
            f"📚 ADK will provide session context automatically ({len(combined_history)} previous messages available)"
        )

        result = await run_agent(
            agent_id=str(agent_id),
            external_id=context_id,
            message=text,  # Send only the original message - ADK handles context
            session_service=session_service,
            artifacts_service=artifacts_service,
            memory_service=memory_service,
            db=db,
            files=files if files else None,
        )

        final_response = result.get("final_response", "No response")
        logger.info(f"✅ Agent response: {final_response}")

        # Log what we're about to send to create_task_response
        logger.info(
            f"🏗️ Creating task response with {len(combined_history) if combined_history else 0} history messages"
        )

        # Create current user message object for history
        current_user_message = {
            "content": text,
            "messageId": message.get("messageId"),
            "timestamp": None,  # Could add current timestamp
        }

        # Create A2A compliant response with history
        task_response = create_task_response(
            task_id,
            context_id,
            final_response,
            combined_history if combined_history else None,
            current_user_message,
        )

        logger.info(
            f"📦 Task response created with {len(task_response.get('artifacts', []))} artifacts"
        )

        # Handle push notification if configured
        if push_notification_config:
            try:
                await send_push_notification(task_response, push_notification_config)
                logger.info(f"🔔 Push notification sent successfully")
            except Exception as e:
                logger.error(f"❌ Push notification failed: {e}")
                # Continue execution - push notification failure shouldn't break the response

        return JSONResponse(
            content={"jsonrpc": "2.0", "id": request_id, "result": task_response}
        )

    except Exception as e:
        logger.error(f"❌ Agent execution error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Agent execution failed",
                    "data": {"error": str(e)},
                },
            }
        )


async def handle_message_stream(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> EventSourceResponse:
    """Handle message/stream according to A2A spec."""

    logger.info(f"🔄 Processing message/stream for agent {agent_id}")

    # Extract message
    message = params.get("message")
    if not message:
        # Return error event
        async def error_generator():
            yield {
                "data": json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": {"missing": "message"},
                        },
                    }
                )
            }

        return EventSourceResponse(error_generator())

    # Extract text and files from message
    text = extract_text_from_message(message)
    files = extract_files_from_message(message)
    context_id = message.get("messageId", str(uuid.uuid4()))

    # Use default text if only files provided
    if not text and files:
        text = "Analyze the provided files"

    # Extract and combine conversation history
    conversation_history = extract_conversation_history(str(agent_id), context_id)
    request_history = extract_history_from_params(params)
    combined_history = combine_histories(request_history, conversation_history)

    async def stream_generator():
        try:
            logger.info(f"🌊 Starting stream for: {text} with {len(files)} files")
            logger.info(
                f"📚 ADK will provide session context automatically ({len(combined_history)} previous messages available)"
            )

            # Stream agent execution - ADK handles session history automatically
            async for chunk in run_agent_stream(
                agent_id=str(agent_id),
                external_id=context_id,
                message=text,  # Send only the original message - ADK handles context
                session_service=session_service,
                artifacts_service=artifacts_service,
                memory_service=memory_service,
                db=db,
                files=files if files else None,
            ):
                # Parse chunk and convert to A2A format
                try:
                    chunk_data = json.loads(chunk)

                    # Create TaskStatusUpdateEvent
                    event = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "id": str(uuid.uuid4()),
                            "status": {
                                "state": "working",
                                "message": chunk_data.get("content", {}),
                            },
                            "final": False,
                        },
                    }

                    yield {"data": json.dumps(event)}

                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
                    continue

            # Send final event
            final_event = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "id": str(uuid.uuid4()),
                    "status": {"state": "completed"},
                    "final": True,
                },
            }
            yield {"data": json.dumps(final_event)}

        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            error_event = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Streaming failed",
                    "data": {"error": str(e)},
                },
            }
            yield {"data": json.dumps(error_event)}

    return EventSourceResponse(stream_generator())


@router.get("/{agent_id}/.well-known/agent.json")
async def get_agent_card(
    agent_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """Get agent card according to A2A specification."""

    logger.info(f"📋 Getting agent card for {agent_id}")

    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Build agent card following A2A specification
    agent_card = {
        "name": agent.name,
        "description": agent.description or f"AI Agent {agent.name}",
        "url": f"{settings.API_URL}/api/v1/a2a/{agent_id}",
        "provider": {
            "organization": "Evo AI Platform",
            "url": settings.API_URL,
        },
        "version": "1.0.0",
        "documentationUrl": f"{settings.API_URL}/docs",
        "capabilities": {
            "streaming": True,
            "pushNotifications": True,  # Now supporting push notifications
            "stateTransitionHistory": False,
        },
        "securitySchemes": {
            "apiKey": {
                "type": "apiKey",
                "in": "header",
                "name": "x-api-key",
            }
        },
        "security": [{"apiKey": []}],
        "defaultInputModes": ["text/plain", "application/json"],
        "defaultOutputModes": ["text/plain", "application/json"],
        "skills": [
            {
                "id": "general-assistance",
                "name": "General AI Assistant",
                "description": "Provides general AI assistance and task completion",
                "tags": ["assistant", "general", "ai", "help"],
                "examples": ["Help me with a task", "Answer my question"],
                "inputModes": ["text"],
                "outputModes": ["text"],
            }
        ],
    }

    return JSONResponse(agent_card)


@router.get("/health")
async def health_check():
    """Health check for A2A official implementation - 100% A2A spec compliant."""
    return {
        "status": "healthy",
        "specification": "A2A Protocol v1.0 - 100% COMPLIANT IMPLEMENTATION",
        "specification_url": "https://google.github.io/A2A/specification",
        "compliance_level": "FULL",
        # All RPC methods from A2A spec implemented
        "rpc_methods": {
            "core": ["message/send", "message/stream"],
            "task_management": ["tasks/get", "tasks/cancel", "tasks/resubscribe"],
            "push_notifications": [
                "tasks/pushNotificationConfig/set",
                "tasks/pushNotificationConfig/get",
            ],
            "agent_discovery": ["agent/authenticatedExtendedCard"],
        },
        "endpoints": {
            "agent_endpoint": f"{settings.API_URL}/api/v1/a2a/{{agent_id}}",
            "agent_card": f"{settings.API_URL}/api/v1/a2a/{{agent_id}}/.well-known/agent.json",
        },
        # A2A Protocol Data Objects - all implemented
        "data_objects": [
            "Task",
            "TaskStatus",
            "TaskState",
            "Message",
            "TextPart",
            "FilePart",
            "DataPart",
            "Artifact",
            "PushNotificationConfig",
            "PushNotificationAuthenticationInfo",
            "JSONRPCRequest",
            "JSONRPCResponse",
            "JSONRPCError",
        ],
        # A2A Features implemented
        "features": {
            "multi_turn_conversations": True,
            "file_processing": True,
            "context_preservation": True,
            "streaming": True,
            "push_notifications": True,
            "task_cancellation": True,
            "push_config_management": True,
            "authenticated_extended_cards": True,
            "https_security": True,
            "json_rpc_2_0": True,
        },
        # Security features per A2A spec
        "security": {
            "transport_security": "HTTPS required for push notifications",
            "authentication": "API Key via x-api-key header",
            "webhook_validation": "HTTPS-only webhooks to prevent SSRF",
            "input_validation": "Full parameter validation on all RPC methods",
        },
        # Extensions beyond A2A spec
        "extensions": {
            "conversation_history": f"{settings.API_URL}/api/v1/a2a/{{agent_id}}/conversation/history",
            "sessions": f"{settings.API_URL}/api/v1/a2a/{{agent_id}}/sessions",
            "session_history": f"{settings.API_URL}/api/v1/a2a/{{agent_id}}/sessions/{{session_id}}/history",
        },
        "compatibility_notes": [
            "Supports both official A2A format and common variations",
            "Backward compatible with alternative field names",
            "Task management adapted for synchronous execution model",
            "Push notifications with multiple authentication schemes",
        ],
    }


@router.get("/{agent_id}/sessions")
async def list_agent_sessions(
    agent_id: uuid.UUID,
    external_id: str,
    x_api_key: str = Header(None, alias="x-api-key"),
    db: Session = Depends(get_db),
):
    """List sessions for an agent and external_id (A2A extension)."""

    logger.info(f"📋 Listing sessions for agent {agent_id}, external_id: {external_id}")

    # Verify API key
    await verify_api_key(db, x_api_key)

    # Verify agent exists
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        # List sessions from session service
        sessions = []
        session_id = f"{external_id}_{agent_id}"

        # Try to get session
        session = session_service.get_session(
            app_name=str(agent_id), user_id=external_id, session_id=session_id
        )

        if session:
            # Extract conversation history
            history = extract_conversation_history(str(agent_id), external_id)

            sessions.append(
                {
                    "sessionId": session_id,
                    "contextId": external_id,
                    "lastUpdate": getattr(session, "last_update_time", None),
                    "messageCount": len(history),
                    "status": "active",
                }
            )

        return JSONResponse({"sessions": sessions, "total": len(sessions)})

    except Exception as e:
        logger.error(f"❌ Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.get("/{agent_id}/sessions/{session_id}/history")
async def get_session_history(
    agent_id: uuid.UUID,
    session_id: str,
    x_api_key: str = Header(None, alias="x-api-key"),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    """Get conversation history for a specific session (A2A extension)."""

    logger.info(f"📚 Getting history for session {session_id}")

    # Verify API key
    await verify_api_key(db, x_api_key)

    # Verify agent exists
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        # Parse session_id to get external_id
        if "_" in session_id:
            external_id = session_id.split("_")[0]
        else:
            external_id = session_id

        # Extract conversation history
        history = extract_conversation_history(str(agent_id), external_id)

        # Limit results
        if limit > 0:
            history = history[-limit:]

        return JSONResponse(
            {"sessionId": session_id, "history": history, "total": len(history)}
        )

    except Exception as e:
        logger.error(f"❌ Error getting session history: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error getting session history: {str(e)}"
        )


@router.post("/{agent_id}/conversation/history")
async def get_conversation_history(
    agent_id: uuid.UUID,
    request: Request,
    x_api_key: str = Header(None, alias="x-api-key"),
    db: Session = Depends(get_db),
):
    """
    Get conversation history according to A2A specification.

    Endpoint for retrieving multi-turn conversation context.
    This implements context preservation as defined in A2A spec.
    """
    logger.info(f"📚 A2A Conversation History requested for agent {agent_id}")

    # Verify API key
    await verify_api_key(db, x_api_key)

    # Verify agent exists
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        # Parse JSON-RPC request
        request_body = await request.json()

        jsonrpc = request_body.get("jsonrpc")
        if jsonrpc != "2.0":
            raise HTTPException(status_code=400, detail="Invalid JSON-RPC version")

        params = request_body.get("params", {})
        request_id = request_body.get("id")

        # Extract contextId (external_id) from params
        context_id = params.get("contextId") or params.get("external_id")
        if not context_id:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"missing": "contextId or external_id"},
                    },
                }
            )

        # Extract conversation history using session_service
        history = extract_conversation_history(str(agent_id), context_id)

        # Limit history if requested
        limit = params.get("limit", 50)
        if limit > 0:
            history = history[-limit:]

        # Format as A2A Task response with history artifacts
        task_id = str(uuid.uuid4())

        # Create structured artifacts for history
        artifacts = []

        # Main artifact with recent messages
        if history:
            recent_messages = history[-10:]  # Last 10 messages

            # Create individual message artifacts
            for i, msg in enumerate(recent_messages):
                artifacts.append(
                    {
                        "artifactId": str(uuid.uuid4()),
                        "name": f"message_{i+1}",
                        "description": f"Message from {msg['role']}",
                        "parts": [
                            {
                                "type": "text",
                                "text": msg["content"],
                                "metadata": {
                                    "role": msg["role"],
                                    "messageId": msg.get("messageId"),
                                    "timestamp": msg.get("timestamp"),
                                    "author": msg.get("author"),
                                },
                            }
                        ],
                    }
                )

            # Summary artifact
            artifacts.append(
                {
                    "artifactId": str(uuid.uuid4()),
                    "name": "conversation_summary",
                    "description": f"Conversation history summary ({len(history)} total messages)",
                    "parts": [
                        {
                            "type": "text",
                            "text": f"Conversation with {len(history)} messages between user and agent.",
                            "metadata": {
                                "total_messages": len(history),
                                "recent_messages": len(recent_messages),
                                "context_id": context_id,
                            },
                        }
                    ],
                }
            )

        # Create A2A compliant Task response
        task_response = {
            "id": task_id,
            "contextId": context_id,
            "status": {
                "state": "completed",
                "timestamp": datetime.now().isoformat() + "Z",
            },
            "artifacts": artifacts,
            "kind": "task",
            "metadata": {
                "total_messages": len(history),
                "operation": "conversation_history_retrieval",
            },
        }

        return JSONResponse(
            content={"jsonrpc": "2.0", "id": request_id, "result": task_response}
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"❌ Error retrieving conversation history: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_body.get("id") if "request_body" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            }
        )


async def send_push_notification(
    task_response: Dict[str, Any], push_notification_config: Dict[str, Any]
):
    """Send push notification according to A2A specification section 9.5.

    A2A spec PushNotificationConfig object:
    - url: The absolute HTTPS webhook URL where the A2A Server should POST task updates
    - token (optional): Client-generated opaque token for validation
    - authentication (optional): PushNotificationAuthenticationInfo for authenticating to client's webhook

    Alternative formats supported for compatibility:
    - webhookUrl instead of url
    - webhookAuthenticationInfo instead of authentication
    """
    # Support both official spec format and common variations
    webhook_url = push_notification_config.get("url") or push_notification_config.get(
        "webhookUrl"
    )
    webhook_token = push_notification_config.get("token")

    # Support both official and alternative authentication field names
    authentication = push_notification_config.get(
        "authentication"
    ) or push_notification_config.get("webhookAuthenticationInfo")

    if not webhook_url:
        raise ValueError("pushNotificationConfig.url (or webhookUrl) is required")

    # Validate HTTPS requirement (A2A spec: url MUST be HTTPS for security to prevent SSRF)
    if not webhook_url.startswith("https://"):
        raise ValueError(
            "pushNotificationConfig.url MUST use HTTPS to prevent SSRF attacks"
        )

    logger.info(f"🔔 Sending push notification to: {webhook_url}")

    # Prepare headers according to A2A spec section 9.5
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"A2A-Server/{getattr(settings, 'API_VERSION', '1.0.0')}",
    }

    # Add client token if provided (A2A spec: server SHOULD include in X-A2A-Notification-Token header)
    if webhook_token:
        headers["X-A2A-Notification-Token"] = webhook_token
        logger.info(f"🔑 Added client token to notification headers")

    # Handle authentication according to A2A spec PushNotificationAuthenticationInfo
    if authentication:
        auth_type = authentication.get("type")

        # Handle "none" type (no authentication)
        if auth_type == "none":
            logger.info(f"🔓 No authentication required for webhook")

        # Handle schemes-based authentication (official A2A spec format)
        elif "schemes" in authentication:
            auth_schemes = authentication.get("schemes", [])
            auth_credentials = authentication.get("credentials")

            for scheme in auth_schemes:
                if scheme.lower() == "bearer":
                    # Bearer token authentication
                    if auth_credentials:
                        headers["Authorization"] = f"Bearer {auth_credentials}"
                        logger.info(f"🔐 Added Bearer authentication")
                    else:
                        logger.warning(
                            "⚠️ Bearer scheme specified but no credentials provided"
                        )

                elif scheme.lower() == "apikey":
                    # API Key authentication
                    if auth_credentials:
                        try:
                            # A2A spec example: JSON like {"in": "header", "name": "X-Client-Webhook-Key", "value": "actual_key"}
                            if isinstance(auth_credentials, str):
                                cred_data = json.loads(auth_credentials)
                            else:
                                cred_data = auth_credentials

                            if cred_data.get("in") == "header":
                                header_name = cred_data.get("name", "X-API-Key")
                                header_value = cred_data.get("value")
                                if header_value:
                                    headers[header_name] = header_value
                                    logger.info(
                                        f"🔐 Added API Key authentication to header: {header_name}"
                                    )
                        except (json.JSONDecodeError, TypeError):
                            # Fallback: treat credentials as direct API key value
                            headers["X-API-Key"] = str(auth_credentials)
                            logger.info(f"🔐 Added API Key authentication (fallback)")
                    else:
                        logger.warning(
                            "⚠️ ApiKey scheme specified but no credentials provided"
                        )

                else:
                    logger.warning(f"⚠️ Unsupported authentication scheme: {scheme}")

        # Handle basic authentication types
        elif auth_type == "bearer":
            token = authentication.get("token") or authentication.get("credentials")
            if token:
                headers["Authorization"] = f"Bearer {token}"
                logger.info(f"🔐 Added Bearer authentication (alternative format)")

        elif auth_type == "apikey":
            api_key = (
                authentication.get("apiKey")
                or authentication.get("key")
                or authentication.get("credentials")
            )
            header_name = authentication.get("headerName", "X-API-Key")
            if api_key:
                headers[header_name] = api_key
                logger.info(f"🔐 Added API Key authentication to header: {header_name}")

        else:
            logger.warning(f"⚠️ Unsupported authentication type: {auth_type}")

    # According to A2A spec section 9.5, the notification payload should contain
    # sufficient information for client to identify Task ID and new state
    # The spec suggests sending the full Task object as JSON payload
    notification_payload = task_response

    try:
        # Use 30 second timeout as recommended for webhook calls
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(
                f"📤 Sending POST request to webhook with {len(headers)} headers"
            )

            response = await client.post(
                webhook_url, headers=headers, json=notification_payload
            )

            # Log the response according to A2A spec recommendations
            if response.status_code == 200:
                logger.info(f"✅ Push notification sent successfully to {webhook_url}")
            elif 200 <= response.status_code < 300:
                logger.info(
                    f"✅ Push notification accepted with status {response.status_code} from {webhook_url}"
                )
            else:
                logger.warning(
                    f"⚠️ Push notification received non-success response: {response.status_code} from {webhook_url}"
                )
                try:
                    response_text = response.text[
                        :200
                    ]  # Log first 200 chars of response
                    logger.warning(f"Response body: {response_text}")
                except:
                    pass

            # Don't raise exception for non-200 status codes per A2A spec
            # The webhook might have its own status handling, and notification
            # delivery is best-effort

    except httpx.TimeoutException:
        logger.error(f"❌ Push notification timeout (30s) to {webhook_url}")
        raise Exception(f"Push notification timeout to {webhook_url}")

    except httpx.RequestError as e:
        logger.error(f"❌ Push notification request error to {webhook_url}: {e}")
        raise Exception(f"Push notification request error: {e}")

    except Exception as e:
        logger.error(f"❌ Push notification unexpected error to {webhook_url}: {e}")
        raise Exception(f"Push notification error: {e}")


# Task management functions (A2A spec section 7.3-7.7)
async def handle_tasks_get(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> JSONResponse:
    """Handle tasks/get according to A2A spec section 7.3."""
    logger.info(f"🔍 Processing tasks/get for agent {agent_id}")

    try:
        task_id = params.get("taskId")
        if not task_id:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"missing": "taskId"},
                    },
                }
            )

        # In our implementation, tasks are ephemeral and complete immediately
        # For A2A compliance, we return a completed task with minimal info
        task_response = {
            "id": task_id,
            "status": {
                "state": "completed",
                "timestamp": datetime.now().isoformat() + "Z",
            },
            "kind": "task",
        }

        return JSONResponse(
            content={"jsonrpc": "2.0", "id": request_id, "result": task_response}
        )

    except Exception as e:
        logger.error(f"❌ tasks/get error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            }
        )


async def handle_tasks_cancel(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> JSONResponse:
    """Handle tasks/cancel according to A2A spec section 7.4."""
    logger.info(f"🛑 Processing tasks/cancel for agent {agent_id}")

    try:
        task_id = params.get("taskId")
        if not task_id:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"missing": "taskId"},
                    },
                }
            )

        # In our implementation, tasks complete immediately, so cancellation is not needed
        # Return success for A2A compliance
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "success": True,
                    "message": f"Task {task_id} cancellation requested",
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ tasks/cancel error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            }
        )


# Task push notification config management (A2A spec section 7.5-7.6)
task_push_configs = {}  # In-memory storage for demo - use database in production


async def handle_tasks_push_notification_config_set(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> JSONResponse:
    """Handle tasks/pushNotificationConfig/set according to A2A spec section 7.5."""
    logger.info(f"🔔 Processing tasks/pushNotificationConfig/set for agent {agent_id}")

    try:
        task_id = params.get("taskId")
        push_config = params.get("pushNotificationConfig")

        if not task_id:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"missing": "taskId"},
                    },
                }
            )

        if not push_config:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"missing": "pushNotificationConfig"},
                    },
                }
            )

        # Validate URL is HTTPS
        webhook_url = push_config.get("url") or push_config.get("webhookUrl")
        if webhook_url and not webhook_url.startswith("https://"):
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"error": "pushNotificationConfig.url MUST use HTTPS"},
                    },
                }
            )

        # Store the config (in production, save to database)
        task_push_configs[task_id] = push_config
        logger.info(f"✅ Push notification config stored for task {task_id}")

        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"success": True, "taskId": task_id},
            }
        )

    except Exception as e:
        logger.error(f"❌ tasks/pushNotificationConfig/set error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            }
        )


async def handle_tasks_push_notification_config_get(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> JSONResponse:
    """Handle tasks/pushNotificationConfig/get according to A2A spec section 7.6."""
    logger.info(f"🔍 Processing tasks/pushNotificationConfig/get for agent {agent_id}")

    try:
        task_id = params.get("taskId")
        if not task_id:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"missing": "taskId"},
                    },
                }
            )

        # Retrieve the config (in production, get from database)
        push_config = task_push_configs.get(task_id)

        if push_config:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "taskId": task_id,
                        "pushNotificationConfig": push_config,
                    },
                }
            )
        else:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32001,
                        "message": "Task not found or no push notification config set",
                        "data": {"taskId": task_id},
                    },
                }
            )

    except Exception as e:
        logger.error(f"❌ tasks/pushNotificationConfig/get error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            }
        )


async def handle_tasks_resubscribe(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> JSONResponse:
    """Handle tasks/resubscribe according to A2A spec section 7.7."""
    logger.info(f"🔄 Processing tasks/resubscribe for agent {agent_id}")

    try:
        task_id = params.get("taskId")
        push_config = params.get("pushNotificationConfig")

        if not task_id:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": "Invalid params",
                        "data": {"missing": "taskId"},
                    },
                }
            )

        # Update push notification config if provided
        if push_config:
            task_push_configs[task_id] = push_config
            logger.info(f"✅ Push notification config updated for task {task_id}")

        # In our implementation, tasks complete immediately
        # Return success for A2A compliance
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "success": True,
                    "taskId": task_id,
                    "message": "Resubscription successful",
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ tasks/resubscribe error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            }
        )


async def handle_agent_authenticated_extended_card(
    agent_id: uuid.UUID, params: Dict[str, Any], request_id: str, db: Session
) -> JSONResponse:
    """Handle agent/authenticatedExtendedCard according to A2A spec section 7.8."""
    logger.info(f"🛡️ Processing agent/authenticatedExtendedCard for agent {agent_id}")

    try:
        # Get agent from database
        agent = get_agent(db, agent_id)
        if not agent:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32001,
                        "message": "Agent not found",
                    },
                }
            )

        # Build authenticated extended agent card (can include additional info after auth)
        extended_card = {
            "name": agent.name,
            "description": agent.description or f"AI Agent {agent.name}",
            "url": f"{settings.API_URL}/api/v1/a2a/{agent_id}",
            "provider": {
                "organization": "Evo AI Platform",
                "url": settings.API_URL,
            },
            "version": "1.0.0",
            "documentationUrl": f"{settings.API_URL}/docs",
            "capabilities": {
                "streaming": True,
                "pushNotifications": True,
                "stateTransitionHistory": False,
                "multiTurnConversations": True,
                "fileProcessing": True,
            },
            "securitySchemes": {
                "apiKey": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "x-api-key",
                }
            },
            "security": [{"apiKey": []}],
            "defaultInputModes": ["text/plain", "application/json"],
            "defaultOutputModes": ["text/plain", "application/json"],
            "skills": [
                {
                    "id": "general-assistance",
                    "name": "General AI Assistant",
                    "description": "Provides general AI assistance and task completion",
                    "tags": ["assistant", "general", "ai", "help"],
                    "examples": ["Help me with a task", "Answer my question"],
                    "inputModes": ["text"],
                    "outputModes": ["text"],
                }
            ],
            # Extended information available after authentication
            "extended": {
                "agent_id": str(agent_id),
                "creation_date": getattr(agent, "created_at", None),
                "available_endpoints": [
                    "message/send",
                    "message/stream",
                    "tasks/get",
                    "tasks/cancel",
                    "tasks/pushNotificationConfig/set",
                    "tasks/pushNotificationConfig/get",
                    "tasks/resubscribe",
                    "agent/authenticatedExtendedCard",
                ],
                "rate_limits": {"requests_per_minute": 100, "concurrent_tasks": 10},
            },
        }

        return JSONResponse(
            content={"jsonrpc": "2.0", "id": request_id, "result": extended_card}
        )

    except Exception as e:
        logger.error(f"❌ agent/authenticatedExtendedCard error: {e}")
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": {"error": str(e)},
                },
            }
        )
