"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: tool_seeder.py                                                        │
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

"""
Script to create default tools:
-
Each with basic configurations for demonstration
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from src.models.models import Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_tools():
    """Create default tools in the system"""
    try:
        # Load environment variables
        load_dotenv()

        # Get database settings
        db_url = os.getenv("POSTGRES_CONNECTION_STRING")
        if not db_url:
            logger.error("Environment variable POSTGRES_CONNECTION_STRING not defined")
            return False

        # Connect to the database
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # Check if there are already tools
            existing_tools = session.query(Tool).all()
            if existing_tools:
                logger.info(f"There are already {len(existing_tools)} tools registered")
                return True

            # Tools definitions
            tools = []

            # Create the tools
            for tool_data in tools:

                tool = Tool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    config_json=tool_data["config_json"],
                    environments=tool_data["environments"],
                )

                session.add(tool)
                logger.info(f"Tool '{tool_data['name']}' created successfully")

            session.commit()
            logger.info("All tools were created successfully")
            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error when creating tools: {str(e)}")
            return False

    except Exception as e:
        logger.error(f"Error when creating tools: {str(e)}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    success = create_tools()
    sys.exit(0 if success else 1)
