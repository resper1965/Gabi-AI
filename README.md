<h1 align="center">Gabi AI - Plataforma de Agentes de IA</h1>

<div align="center">

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](./LICENSE)

</div>

## Gabi AI - Plataforma de Agentes de IA

Esta é uma aplicação baseada no Evo AI, agora personalizada como Gabi AI, uma plataforma open-source para criar e gerenciar agentes de IA, permitindo integração com diferentes modelos e serviços de IA.

## 🚀 Visão Geral

A plataforma permite:

- Criação e gerenciamento de agentes de IA
- Integração com diferentes modelos de linguagem
- Gerenciamento de clientes e configuração de servidores MCP
- Gerenciamento de ferramentas personalizadas
- **[Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)**: Framework base para desenvolvimento de agentes
- **[CrewAI Support](https://github.com/crewAI/crewAI)**: Framework alternativo para desenvolvimento de agentes (em desenvolvimento)
- Autenticação JWT com verificação de email
- **[Agent 2 Agent (A2A) Protocol Support](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)**: Interoperabilidade entre agentes de IA
- **[Workflow Agent with LangGraph](https://www.langchain.com/langgraph)**: Construção de workflows complexos de agentes
- **Secure API Key Management**: Armazenamento criptografado de chaves de API
- **Agent Organization**: Estrutura de pastas para organizar agentes por categorias

## 🤖 Agent Types

Gabi AI supports different types of agents that can be flexibly combined:

### 1. LLM Agent (Language Model)

Agent based on language models like GPT-4, Claude, etc. Can be configured with tools, MCP servers, and sub-agents.

### 2. A2A Agent (Agent-to-Agent)

Agent that implements Google's A2A protocol for agent interoperability.

### 3. Sequential Agent

Executes a sequence of sub-agents in a specific order.

### 4. Parallel Agent

Executes multiple sub-agents simultaneously.

### 5. Loop Agent

Executes sub-agents in a loop with a defined maximum number of iterations.

### 6. Workflow Agent

Executes sub-agents in a custom workflow defined by a graph structure using LangGraph.

### 7. Task Agent

Executes a specific task using a target agent with structured task instructions.

## 🛠️ Technologies

### Backend
- **FastAPI**: Web framework for building the API
- **SQLAlchemy**: ORM for database interaction
- **PostgreSQL**: Main database
- **Alembic**: Migration system
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **Redis**: Cache and session management
- **JWT**: Secure token authentication
- **SendGrid/SMTP**: Email service for notifications (configurable)
- **Jinja2**: Template engine for email rendering
- **Bcrypt**: Password hashing and security
- **LangGraph**: Framework for building stateful, multi-agent workflows

### Frontend
- **Next.js 15**: React framework with App Router
- **React 18**: User interface library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern component library
- **React Hook Form**: Form management
- **Zod**: Schema validation
- **ReactFlow**: Node-based visual workflows
- **React Query**: Server state management

## 📊 Langfuse Integration (Tracing & Observability)

Gabi AI platform natively supports integration with [Langfuse](https://langfuse.com/) for detailed tracing of agent executions, prompts, model responses, and tool calls, using the OpenTelemetry (OTel) standard.

### How to configure

1. **Set environment variables in your `.env`:**

   ```env
   LANGFUSE_PUBLIC_KEY="pk-lf-..."
   LANGFUSE_SECRET_KEY="sk-lf-..."
   OTEL_EXPORTER_OTLP_ENDPOINT="https://cloud.langfuse.com/api/public/otel"
   ```

2. **View in the Langfuse dashboard**
   - Access your Langfuse dashboard to see real-time traces.

## 🤖 Agent 2 Agent (A2A) Protocol Support

Gabi AI implements the Google's Agent 2 Agent (A2A) protocol, enabling seamless communication and interoperability between AI agents.

For more information about the A2A protocol, visit [Google's A2A Protocol Documentation](https://google.github.io/A2A/).

## 📋 Prerequisites

### Backend
- **Python**: 3.10 or higher
- **PostgreSQL**: 13.0 or higher
- **Redis**: 6.0 or higher
- **Git**: For version control
- **Make**: For running Makefile commands

### Frontend
- **Node.js**: 18.0 or higher
- **pnpm**: Package manager (recommended) or npm/yarn

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/resper1965/Gabi-AI.git
cd gabi-ai
```

### 2. Backend Setup

#### Virtual Environment and Dependencies

```bash
# Create and activate virtual environment
make venv
source venv/bin/activate  # Linux/Mac
# or on Windows: venv\Scripts\activate

# Install development dependencies
make install-dev
```

#### Environment Configuration

```bash
# Copy and configure backend environment
cp .env.example .env
# Edit the .env file with your database, Redis, and other settings
```

#### Database Setup

```bash
# Initialize database and apply migrations
make alembic-upgrade

# Seed initial data (admin user, sample clients, etc.)
make seed-all
```

### 3. Frontend Setup

#### Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies using pnpm (recommended)
pnpm install

# Or using npm
# npm install

# Or using yarn
# yarn install
```

#### Frontend Environment Configuration

```bash
# Copy and configure frontend environment
cp .env.example .env
# Edit .env with your API URL (default: http://localhost:8000)
```

The frontend `.env` should contain:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Running the Application

### Development Mode

#### Start Backend (Terminal 1)
```bash
# From project root
make run
# Backend will be available at http://localhost:8000
```

#### Start Frontend (Terminal 2)
```bash
# From frontend directory
cd frontend
pnpm dev

# Or using npm/yarn
# npm run dev
# yarn dev

# Frontend will be available at http://localhost:3000
```

### Production Mode

#### Backend
```bash
make run-prod    # Production with multiple workers
```

#### Frontend
```bash
cd frontend
pnpm build && pnpm start

# Or using npm/yarn
# npm run build && npm start
# yarn build && yarn start
```

## 🐳 Docker Installation

### Full Stack with Docker Compose

```bash
# Build and start all services (backend + database + redis)
make docker-build
make docker-up

# Initialize database with seed data
make docker-seed
```

### Frontend with Docker

```bash
# From frontend directory
cd frontend

# Build frontend image
docker build -t gabi-ai-frontend .

# Run frontend container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 gabi-ai-frontend
```

Or using the provided docker-compose:

```bash
# From frontend directory
cd frontend
docker-compose up -d
```

## 🎯 Getting Started

After installation, follow these steps:

1. **Access the Frontend**: Open `http://localhost:3000`
2. **Create Admin Account**: Use the seeded admin credentials or register a new account
3. **Configure MCP Server**: Set up your first MCP server connection
4. **Create Client**: Add a client to organize your agents
5. **Build Your First Agent**: Create and configure your AI agent
6. **Test Agent**: Use the chat interface to interact with your agent

### Default Admin Credentials

After running the seeders, you can login with:
- **Email**: Check the seeder output for the generated admin email
- **Password**: Check the seeder output for the generated password

## 🖥️ API Documentation

The interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 👨‍💻 Development Commands

### Backend Commands
```bash
# Database migrations
make alembic-upgrade            # Update database to latest version
make alembic-revision message="description"  # Create new migration

# Seeders
make seed-all                   # Run all seeders

# Code verification
make lint                       # Verify code with flake8
make format                     # Format code with black
```

### Frontend Commands
```bash
# From frontend directory
cd frontend

# Development
pnpm dev                        # Start development server
pnpm build                      # Build for production
pnpm start                      # Start production server
pnpm lint                       # Run ESLint
```

## 🚀 Configuration

### Backend Configuration (.env file)

Key settings include:

```bash
# Database settings
POSTGRES_CONNECTION_STRING="postgresql://postgres:root@localhost:5432/gabi_ai"

# Redis settings
REDIS_HOST="localhost"
REDIS_PORT=6379

# AI Engine configuration
AI_ENGINE="adk"  # Options: "adk" (Google Agent Development Kit) or "crewai" (CrewAI framework)

# JWT settings
JWT_SECRET_KEY="your-jwt-secret-key"

# Email provider configuration
EMAIL_PROVIDER="sendgrid"  # Options: "sendgrid" or "smtp"

# Encryption for API keys
ENCRYPTION_KEY="your-encryption-key"
```

### Frontend Configuration (.env file)

```bash
# API Configuration
NEXT_PUBLIC_API_URL="http://localhost:8000"  # Backend API URL
```

> **Note**: While Google ADK is fully supported, the CrewAI engine option is still under active development. For production environments, it's recommended to use the default "adk" engine.

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication with:

- User registration and email verification
- Login to obtain JWT tokens
- Password recovery flow
- Account lockout after multiple failed login attempts

## 🚀 Star Us on GitHub

If you find Gabi AI useful, please consider giving us a star! Your support helps us grow our community and continue improving the product.

[![Star History Chart](https://api.star-history.com/svg?repos=resper1965/Gabi-AI&type=Date)](https://www.star-history.com/#resper1965/Gabi-AI&Date)

## 🤝 Contributing

We welcome contributions from the community! Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 📄 License

This project is licensed under the [Apache License 2.0](./LICENSE).
