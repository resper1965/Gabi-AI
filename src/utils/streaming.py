"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: streaming.py                                                          │
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

import asyncio
from typing import AsyncGenerator
from fastapi import HTTPException


class SSEUtils:
    @staticmethod
    async def with_timeout(
        generator: AsyncGenerator, timeout: int = 30, retry_attempts: int = 3
    ) -> AsyncGenerator:
        """
        Adds timeout and retry to an SSE event generator.

        Args:
            generator: Event generator
            timeout: Maximum wait time in seconds
            retry_attempts: Number of reconnection attempts

        Yields:
            Events from the generator
        """
        attempts = 0
        while attempts < retry_attempts:
            try:
                async for event in asyncio.wait_for(generator, timeout):
                    yield event
                break
            except asyncio.TimeoutError:
                attempts += 1
                if attempts >= retry_attempts:
                    raise HTTPException(
                        status_code=408, detail="Timeout after multiple attempts"
                    )
                await asyncio.sleep(1)  # Wait before trying again

    @staticmethod
    def format_error_event(error: Exception) -> str:
        """
        Formats an SSE error event.

        Args:
            error: Occurred exception

        Returns:
            Formatted SSE error event
        """
        return f"event: error\ndata: {str(error)}\n\n"

    @staticmethod
    def validate_sse_headers(headers: dict) -> None:
        """
        Validates required headers for SSE.

        Args:
            headers: Dictionary of headers

        Raises:
            HTTPException if invalid headers
        """
        required_headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }

        for header, value in required_headers.items():
            if headers.get(header) != value:
                raise HTTPException(
                    status_code=400, detail=f"Invalid or missing header: {header}"
                )
