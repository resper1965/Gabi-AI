"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: tool_service.py                                                       │
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
from fastapi import HTTPException, status
from src.models.models import Tool
from src.schemas.schemas import ToolCreate
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


def get_tool(db: Session, tool_id: uuid.UUID) -> Optional[Tool]:
    """Search for a tool by ID"""
    try:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            logger.warning(f"Tool not found: {tool_id}")
            return None
        return tool
    except SQLAlchemyError as e:
        logger.error(f"Error searching for tool {tool_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for tool",
        )


def get_tools(db: Session, skip: int = 0, limit: int = 100) -> List[Tool]:
    """Search for all tools with pagination"""
    try:
        return db.query(Tool).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error searching for tools: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching for tools",
        )


def create_tool(db: Session, tool: ToolCreate) -> Tool:
    """Creates a new tool"""
    try:
        db_tool = Tool(**tool.model_dump())
        db.add(db_tool)
        db.commit()
        db.refresh(db_tool)
        logger.info(f"Tool created successfully: {db_tool.id}")
        return db_tool
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating tool: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating tool",
        )


def update_tool(db: Session, tool_id: uuid.UUID, tool: ToolCreate) -> Optional[Tool]:
    """Updates an existing tool"""
    try:
        db_tool = get_tool(db, tool_id)
        if not db_tool:
            return None

        for key, value in tool.model_dump().items():
            setattr(db_tool, key, value)

        db.commit()
        db.refresh(db_tool)
        logger.info(f"Tool updated successfully: {tool_id}")
        return db_tool
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating tool {tool_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating tool",
        )


def delete_tool(db: Session, tool_id: uuid.UUID) -> bool:
    """Remove a tool"""
    try:
        db_tool = get_tool(db, tool_id)
        if not db_tool:
            return False

        db.delete(db_tool)
        db.commit()
        logger.info(f"Tool removed successfully: {tool_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error removing tool {tool_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing tool",
        )
