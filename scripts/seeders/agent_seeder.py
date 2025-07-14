"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ @author: Davidson Gomes                                                      │
│ @file: agent_seeder.py                                                       │
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
Script to create demo agents:
- Assistant Agent (LLM)
- Research Agent (A2A)
- Workflow Agent (Workflow)
Each with basic configurations for demonstration
"""

import os
import sys
import logging
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from src.models.models import Agent, Client, User

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_demo_agents():
    """Create demo agents in the system"""
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
            # Check if there are already agents
            existing_agents = session.query(Agent).all()
            if existing_agents:
                logger.info(f"There are already {len(existing_agents)} agents registered")
                return True

            # Get admin user to associate with agents
            admin_email = os.getenv("ADMIN_EMAIL", "resper@ness.com.br")
            admin_user = session.query(User).filter(User.email == admin_email).first()
            
            if not admin_user:
                logger.error(f"Admin user with email {admin_email} not found")
                return False

            # Get or create a client for the admin
            client = session.query(Client).filter(Client.id == admin_user.client_id).first()
            if not client:
                # Create a default client for admin
                client = Client(
                    name="Gabi AI Admin",
                    email=admin_email
                )
                session.add(client)
                session.flush()
                admin_user.client_id = client.id
                session.commit()

            # Demo agents definitions
            demo_agents = [
                {
                    "name": "Gabi Assistant",
                    "type": "llm",
                    "description": "Assistente inteligente para ajudar com tarefas gerais e responder perguntas",
                    "role": "Assistente Virtual",
                    "goal": "Ajudar usuários com informações e tarefas do dia a dia",
                    "instruction": "Você é o Gabi Assistant, um assistente virtual amigável e útil. Sempre seja educado e forneça informações precisas.",
                    "model": "gpt-4",
                    "config": {
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "system_prompt": "Você é o Gabi Assistant, um assistente virtual inteligente e amigável."
                    }
                },
                {
                    "name": "Research Agent",
                    "type": "a2a",
                    "description": "Agente especializado em pesquisa e busca de informações",
                    "role": "Pesquisador",
                    "goal": "Realizar pesquisas profundas e fornecer informações detalhadas",
                    "instruction": "Você é um agente de pesquisa especializado. Use ferramentas de busca para encontrar informações precisas e relevantes.",
                    "model": "claude-3-sonnet",
                    "config": {
                        "temperature": 0.3,
                        "max_tokens": 3000,
                        "tools": ["web_search", "file_reader"]
                    }
                },
                {
                    "name": "Workflow Manager",
                    "type": "workflow",
                    "description": "Agente para gerenciar fluxos de trabalho complexos",
                    "role": "Gerente de Workflow",
                    "goal": "Orquestrar tarefas complexas e coordenar múltiplos agentes",
                    "instruction": "Você é um gerente de workflow. Coordene tarefas complexas e garanta que todos os passos sejam executados corretamente.",
                    "model": "gpt-4",
                    "config": {
                        "temperature": 0.5,
                        "max_tokens": 2500,
                        "workflow_steps": ["planning", "execution", "review"]
                    }
                },
                {
                    "name": "Task Agent",
                    "type": "task",
                    "description": "Agente especializado em execução de tarefas específicas",
                    "role": "Executor de Tarefas",
                    "goal": "Executar tarefas específicas de forma eficiente e precisa",
                    "instruction": "Você é um agente de tarefas. Foque em executar uma tarefa específica de forma eficiente e precisa.",
                    "model": "gpt-3.5-turbo",
                    "config": {
                        "temperature": 0.2,
                        "max_tokens": 1500,
                        "task_type": "execution"
                    }
                }
            ]

            # Create the agents
            for agent_data in demo_agents:
                agent = Agent(
                    id=uuid.uuid4(),
                    client_id=client.id,
                    name=agent_data["name"],
                    type=agent_data["type"],
                    description=agent_data["description"],
                    role=agent_data["role"],
                    goal=agent_data["goal"],
                    instruction=agent_data["instruction"],
                    model=agent_data["model"],
                    config=agent_data["config"]
                )

                session.add(agent)
                logger.info(f"Agent '{agent_data['name']}' created successfully")

            session.commit()
            logger.info("All demo agents were created successfully")
            return True

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error when creating demo agents: {str(e)}")
            return False

    except Exception as e:
        logger.error(f"Error when creating demo agents: {str(e)}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    success = create_demo_agents()
    sys.exit(0 if success else 1) 