"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: agent_runner.py                                                       │
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

from crewai import Crew, Task, Agent as LlmAgent
from src.services.crewai.session_service import (
    CrewSessionService,
    Event,
    Content,
    Part,
    Session,
)
from src.services.crewai.agent_builder import AgentBuilder
from src.utils.logger import setup_logger
from src.core.exceptions import AgentNotFoundError, InternalServerError
from src.services.agent_service import get_agent
from sqlalchemy.orm import Session
from typing import Optional, AsyncGenerator
import asyncio
import json
from datetime import datetime
from src.utils.otel import get_tracer
from opentelemetry import trace
import base64

logger = setup_logger(__name__)


def extract_text_from_output(crew_output):
    """Extract text from CrewOutput object."""
    if hasattr(crew_output, "raw") and crew_output.raw:
        return crew_output.raw
    elif hasattr(crew_output, "__str__"):
        return str(crew_output)

    # Fallback if no text found
    return "Unable to extract a valid response."


async def run_agent(
    agent_id: str,
    external_id: str,
    message: str,
    session_service: CrewSessionService,
    db: Session,
    session_id: Optional[str] = None,
    timeout: float = 60.0,
    files: Optional[list] = None,
):
    tracer = get_tracer()
    with tracer.start_as_current_span(
        "run_agent",
        attributes={
            "agent_id": agent_id,
            "external_id": external_id,
            "session_id": session_id or f"{external_id}_{agent_id}",
            "message": message,
            "has_files": files is not None and len(files) > 0,
        },
    ):
        exit_stack = None
        try:
            logger.info(
                f"Starting execution of agent {agent_id} for external_id {external_id}"
            )
            logger.info(f"Received message: {message}")

            if files and len(files) > 0:
                logger.info(f"Received {len(files)} files with message")

            get_root_agent = get_agent(db, agent_id)
            logger.info(
                f"Root agent found: {get_root_agent.name} (type: {get_root_agent.type})"
            )

            if get_root_agent is None:
                raise AgentNotFoundError(f"Agent with ID {agent_id} not found")

            # Using the AgentBuilder to create the agent
            agent_builder = AgentBuilder(db)
            result = await agent_builder.build_agent(get_root_agent)

            # Check how the result is structured
            if isinstance(result, tuple) and len(result) == 2:
                root_agent, exit_stack = result
            else:
                # If the result is not a tuple of 2 elements
                root_agent = result
                exit_stack = None
                logger.warning("build_agent did not return an exit_stack")

            # TODO: files should be processed here

            # Fetch session information
            crew_session_id = f"{external_id}_{agent_id}"
            if session_id is None:
                session_id = crew_session_id

            logger.info(f"Searching session for external_id {external_id}")
            try:
                session = session_service.get_session(
                    agent_id=agent_id,
                    external_id=external_id,
                    session_id=crew_session_id,
                )
            except Exception as e:
                logger.warning(f"Error getting session: {str(e)}")
                session = None

            if session is None:
                logger.info(f"Creating new session for external_id {external_id}")
                session = session_service.create_session(
                    agent_id=agent_id,
                    external_id=external_id,
                    session_id=crew_session_id,
                )

            # Add user message to session
            session.events.append(
                Event(
                    author="user",
                    content=Content(parts=[{"text": message}]),
                    timestamp=datetime.now().timestamp(),
                )
            )

            # Save session to database
            session_service.save_session(session)

            # Build message history for context
            conversation_history = []
            if session and session.events:
                for event in session.events:
                    if event.author and event.content and event.content.parts:
                        for part in event.content.parts:
                            if isinstance(part, dict) and "text" in part:
                                role = "User" if event.author == "user" else "Assistant"
                                conversation_history.append(f"{role}: {part['text']}")

            # Build description with history as context
            task_description = (
                f"Conversation history:\n" + "\n".join(conversation_history)
                if conversation_history
                else ""
            )
            task_description += f"\n\nCurrent user message: {message}"

            task = Task(
                name="resolve_user_request",
                description=task_description,
                expected_output="Response to the user request",
                agent=root_agent,
                verbose=True,
            )

            crew = await agent_builder.build_crew([root_agent], [task])

            # Use normal kickoff or kickoff_async instead of kickoff_for_each
            if hasattr(crew, "kickoff_async"):
                crew_output = await crew.kickoff_async(inputs={"message": message})
            else:
                loop = asyncio.get_event_loop()
                crew_output = await loop.run_in_executor(
                    None, lambda: crew.kickoff(inputs={"message": message})
                )

            # Extract response and add to session
            final_text = extract_text_from_output(crew_output)

            # Add agent response as event in session
            session.events.append(
                Event(
                    author=get_root_agent.name,
                    content=Content(parts=[{"text": final_text}]),
                    timestamp=datetime.now().timestamp(),
                )
            )

            # Save session with new event
            session_service.save_session(session)

            logger.info("Starting agent execution")

            final_response_text = "No final response captured."
            message_history = []

            try:
                response_queue = asyncio.Queue()
                execution_completed = asyncio.Event()

                async def process_events():
                    try:
                        # Log the result
                        logger.info(f"Crew output: {crew_output}")

                        # Signal that execution is complete
                        execution_completed.set()

                        # Extract text from CrewOutput object
                        final_text = "Unable to extract a valid response."

                        if hasattr(crew_output, "raw") and crew_output.raw:
                            final_text = crew_output.raw
                        elif hasattr(crew_output, "__str__"):
                            final_text = str(crew_output)

                        # If still empty or None, check crew artifacts
                        if not final_text or final_text.strip() == "":
                            # Try to get from agent messages
                            if hasattr(root_agent, "messages") and root_agent.messages:
                                # Get the last message from the agent
                                for msg in reversed(root_agent.messages):
                                    if hasattr(msg, "content") and msg.content:
                                        final_text = msg.content
                                        break

                            # If still empty, use a fallback
                            if not final_text or final_text.strip() == "":
                                final_text = "The agent could not produce a valid response. Please try again with a different question."

                        # Put the extracted text in the queue
                        await response_queue.put(final_text)
                    except Exception as e:
                        logger.error(f"Error in process_events: {str(e)}")
                        # Provide a more helpful error response
                        error_response = f"An error occurred during processing: {str(e)}\n\nIf you are trying to use external tools such as Brave Search, please make sure the connection is working properly."
                        await response_queue.put(error_response)
                        execution_completed.set()

                task = asyncio.create_task(process_events())

                try:
                    wait_task = asyncio.create_task(execution_completed.wait())
                    done, pending = await asyncio.wait({wait_task}, timeout=timeout)

                    for p in pending:
                        p.cancel()

                    if not execution_completed.is_set():
                        logger.warning(
                            f"Agent execution timed out after {timeout} seconds"
                        )
                        await response_queue.put(
                            "The response took too long and was interrupted."
                        )

                    final_response_text = await response_queue.get()

                except Exception as e:
                    logger.error(f"Error waiting for response: {str(e)}")
                    final_response_text = f"Error processing response: {str(e)}"

                # Add the session to memory after completion
                # completed_session = session_service.get_session(
                #     app_name=agent_id,
                #     user_id=external_id,
                #     session_id=crew_session_id,
                # )

                # memory_service.add_session_to_memory(completed_session)

                # Cancel the processing task if it is still running
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        logger.info("Task cancelled successfully")
                    except Exception as e:
                        logger.error(f"Error cancelling task: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                raise InternalServerError(str(e)) from e

            logger.info("Agent execution completed successfully")
            return {
                "final_response": final_response_text,
                "message_history": message_history,
            }
        except AgentNotFoundError as e:
            logger.error(f"Error processing request: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Internal error processing request: {str(e)}", exc_info=True)
            raise InternalServerError(str(e))
        finally:
            # Clean up MCP connection - MUST be executed in the same task
            if exit_stack:
                logger.info("Closing MCP server connection...")
                try:
                    if hasattr(exit_stack, "aclose"):
                        # If it's an AsyncExitStack
                        await exit_stack.aclose()
                    elif isinstance(exit_stack, list):
                        # If it's a list of adapters
                        for adapter in exit_stack:
                            if hasattr(adapter, "close"):
                                adapter.close()
                except Exception as e:
                    logger.error(f"Error closing MCP connection: {e}")
                    # Do not raise the exception to not obscure the original error


def convert_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: convert_sets(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets(i) for i in obj]
    else:
        return obj


async def run_agent_stream(
    agent_id: str,
    external_id: str,
    message: str,
    db: Session,
    session_id: Optional[str] = None,
    files: Optional[list] = None,
) -> AsyncGenerator[str, None]:
    tracer = get_tracer()
    span = tracer.start_span(
        "run_agent_stream",
        attributes={
            "agent_id": agent_id,
            "external_id": external_id,
            "session_id": session_id or f"{external_id}_{agent_id}",
            "message": message,
            "has_files": files is not None and len(files) > 0,
        },
    )
    exit_stack = None
    try:
        with trace.use_span(span, end_on_exit=True):
            try:
                logger.info(
                    f"Starting streaming execution of agent {agent_id} for external_id {external_id}"
                )
                logger.info(f"Received message: {message}")

                if files and len(files) > 0:
                    logger.info(f"Received {len(files)} files with message")

                get_root_agent = get_agent(db, agent_id)
                logger.info(
                    f"Root agent found: {get_root_agent.name} (type: {get_root_agent.type})"
                )

                if get_root_agent is None:
                    raise AgentNotFoundError(f"Agent with ID {agent_id} not found")

                # Using the AgentBuilder to create the agent
                agent_builder = AgentBuilder(db)
                result = await agent_builder.build_agent(get_root_agent)

                # Check how the result is structured
                if isinstance(result, tuple) and len(result) == 2:
                    root_agent, exit_stack = result
                else:
                    # If the result is not a tuple of 2 elements
                    root_agent = result
                    exit_stack = None
                    logger.warning("build_agent did not return an exit_stack")

                # TODO: files should be processed here

                # Fetch session history if available
                session_id = f"{external_id}_{agent_id}"

                # Create an instance of the session service
                try:
                    from src.config.settings import get_settings

                    settings = get_settings()
                    db_url = settings.DATABASE_URL
                except ImportError:
                    # Fallback to local SQLite if cannot import settings
                    db_url = "sqlite:///data/crew_sessions.db"

                session_service = CrewSessionService(db_url)

                try:
                    # Try to get existing session
                    session = session_service.get_session(
                        agent_id=agent_id,
                        external_id=external_id,
                        session_id=session_id,
                    )
                except Exception as e:
                    logger.warning(f"Could not load session: {e}")
                    session = None

                # Build message history for context
                conversation_history = []

                if session and session.events:
                    for event in session.events:
                        if event.author and event.content and event.content.parts:
                            for part in event.content.parts:
                                if isinstance(part, dict) and "text" in part:
                                    role = (
                                        "User"
                                        if event.author == "user"
                                        else "Assistant"
                                    )
                                    conversation_history.append(
                                        f"{role}: {part['text']}"
                                    )

                # Build description with history
                task_description = (
                    f"Conversation history:\n" + "\n".join(conversation_history)
                    if conversation_history
                    else ""
                )
                task_description += f"\n\nCurrent user message: {message}"

                task = Task(
                    name="resolve_user_request",
                    description=task_description,
                    expected_output="Response to the user request",
                    agent=root_agent,
                    verbose=True,
                )

                crew = await agent_builder.build_crew([root_agent], [task])

                logger.info("Starting agent streaming execution")

                try:
                    # Check if we can process messages with kickoff_for_each
                    if hasattr(crew, "kickoff_for_each"):
                        # Create input with current message
                        inputs = [{"message": message}]
                        logger.info(
                            f"Using kickoff_for_each for streaming with {len(inputs)} input(s)"
                        )

                        # Execute kickoff_for_each
                        results = crew.kickoff_for_each(inputs=inputs)

                        # Print results and save to session
                        for i, result in enumerate(results):
                            logger.info(f"Result of event {i+1}: {result}")

                            # If we have a session, save the response to it
                            if session:
                                # Add agent response as event
                                session.events.append(
                                    Event(
                                        author="agent",
                                        content=Content(parts=[{"text": result}]),
                                        timestamp=datetime.now().timestamp(),
                                    )
                                )

                        # Save current session with new message
                        if session:
                            # Also add user message if it doesn't exist yet
                            if not any(
                                e.author == "user"
                                and any(
                                    p.get("text") == message for p in e.content.parts
                                )
                                for e in session.events
                                if e.content and e.content.parts
                            ):
                                session.events.append(
                                    Event(
                                        author="user",
                                        content=Content(parts=[{"text": message}]),
                                        timestamp=datetime.now().timestamp(),
                                    )
                                )
                            # Save session
                            try:
                                session_service.save_session(session)
                                logger.info(f"Session saved successfully: {session_id}")
                            except Exception as e:
                                logger.error(f"Error saving session: {e}")

                        # Use last result as final output
                        crew_output = results[-1] if results else None
                    else:
                        # CrewAI kickoff method is synchronous, fallback if kickoff_for_each not available
                        logger.info(
                            "kickoff_for_each not available, using standard kickoff for streaming"
                        )
                        crew_output = crew.kickoff()

                    logger.info(f"Crew output: {crew_output}")

                    # Extract the actual text content
                    if hasattr(crew_output, "raw") and crew_output.raw:
                        final_output = crew_output.raw
                    elif hasattr(crew_output, "__str__"):
                        final_output = str(crew_output)
                    else:
                        final_output = "Could not extract text from response"

                    # Save response to session (for fallback case of normal kickoff)
                    if session and not hasattr(crew, "kickoff_for_each"):
                        # Add agent response
                        session.events.append(
                            Event(
                                author="agent",
                                content=Content(parts=[{"text": final_output}]),
                                timestamp=datetime.now().timestamp(),
                            )
                        )

                        # Add user message if it doesn't exist yet
                        if not any(
                            e.author == "user"
                            and any(p.get("text") == message for p in e.content.parts)
                            for e in session.events
                            if e.content and e.content.parts
                        ):
                            session.events.append(
                                Event(
                                    author="user",
                                    content=Content(parts=[{"text": message}]),
                                    timestamp=datetime.now().timestamp(),
                                )
                            )

                        # Save session
                        try:
                            session_service.save_session(session)
                            logger.info(
                                f"Session saved successfully (method: kickoff): {session_id}"
                            )
                        except Exception as e:
                            logger.error(f"Error saving session: {e}")

                    yield json.dumps({"text": final_output})
                except Exception as e:
                    logger.error(f"Error processing request: {str(e)}")
                    raise InternalServerError(str(e)) from e
                finally:
                    # Clean up MCP connection
                    if exit_stack:
                        logger.info("Closing MCP server connection...")
                        try:
                            if hasattr(exit_stack, "aclose"):
                                # If it's an AsyncExitStack
                                await exit_stack.aclose()
                            elif isinstance(exit_stack, list):
                                # If it's a list of adapters
                                for adapter in exit_stack:
                                    if hasattr(adapter, "close"):
                                        adapter.close()
                        except Exception as e:
                            logger.error(f"Error closing MCP connection: {e}")
                            # Do not raise the exception to not obscure the original error

                logger.info("Agent streaming execution completed successfully")
            except AgentNotFoundError as e:
                logger.error(f"Error processing request: {str(e)}")
                raise InternalServerError(str(e)) from e
            except Exception as e:
                logger.error(
                    f"Internal error processing request: {str(e)}", exc_info=True
                )
                raise InternalServerError(str(e))
    finally:
        span.end()
