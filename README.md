# 🚀 Gabi Agent - Plataforma de Agentes de IA

<div align="center">

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](./LICENSE)
[![EasyPanel](https://img.shields.io/badge/EasyPanel-Template-brightgreen)](https://easypanel.io)

</div>

## 📖 Sobre

**Gabi Agent** é uma plataforma open-source para criar e gerenciar agentes de IA, permitindo integração com diferentes modelos e serviços de IA. Baseada em tecnologias modernas, oferece uma interface intuitiva para desenvolvimento e deploy de agentes inteligentes.

## ✨ Características Principais

- 🤖 **Múltiplos Tipos de Agentes**: LLM, A2A, Sequential, Parallel, Loop, Workflow, Task
- 🔧 **Integração Flexível**: OpenAI, Anthropic, Google ADK, CrewAI
- 🛡️ **Segurança**: JWT Authentication, API Key Management, Email Verification
- 📊 **Observabilidade**: Langfuse Integration, OpenTelemetry
- 🎨 **Interface Moderna**: Next.js 15, React 18, Tailwind CSS
- 🐳 **Container Ready**: Docker & EasyPanel Support
- 🔄 **A2A Protocol**: Agent-to-Agent interoperability
- 📈 **Workflow Builder**: Visual workflow creation with LangGraph

## 🚀 Instalação Rápida

### Via EasyPanel (Recomendado)

1. **Acesse o EasyPanel** na sua VPS
2. **Crie um novo projeto** e selecione "Template"
3. **Escolha "Gabi Agent"** na lista de templates
4. **Configure as variáveis** de ambiente
5. **Deploy automático** - pronto para usar!

### Instalação Manual

#### Pré-requisitos
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+

#### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/resper1965/Gabi-Agent.git
cd gabi-agent

# 2. Configure o ambiente
cp env.easypanel.example .env
# Edite o arquivo .env com suas configurações

# 3. Execute o script de setup
bash scripts/easypanel-setup.sh

# 4. Inicie com Docker Compose
docker-compose up -d
```

## 🛠️ Tecnologias

### Backend
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Redis** - Cache
- **JWT** - Authentication
- **LangGraph** - Workflows

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - Components
- **ReactFlow** - Workflows

## 📋 Configuração

### Variáveis de Ambiente Essenciais

```env
# Database
POSTGRES_PASSWORD=sua-senha-segura
POSTGRES_DB=gabi_agent

# Application
SECRET_KEY=sua-chave-secreta
ADMIN_EMAIL=admin@exemplo.com
ADMIN_PASSWORD=senha-admin

# AI APIs (opcionais)
OPENAI_API_KEY=sua-chave-openai
ANTHROPIC_API_KEY=sua-chave-anthropic

# Email (opcional)
SENDGRID_API_KEY=sua-chave-sendgrid
```

## 🎯 Primeiro Acesso

1. **Acesse**: `http://seu-dominio.com` ou `http://localhost:3000`
2. **Login**: Use as credenciais configuradas em `ADMIN_EMAIL` e `ADMIN_PASSWORD`
3. **Configure**: MCP servers, clientes e agentes
4. **Teste**: Use o chat para interagir com seus agentes

## 📚 Documentação

- **API Docs**: `http://localhost:8000/docs`
- **Instalação EasyPanel**: [INSTALACAO_EASYPANEL.md](./INSTALACAO_EASYPANEL.md)
- **Desenvolvimento**: [DEVELOPMENT.md](./DEVELOPMENT.md)

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
make run              # Iniciar backend
cd frontend && pnpm dev  # Iniciar frontend

# Docker
docker-compose up -d  # Iniciar todos os serviços
docker-compose logs   # Ver logs

# Database
make alembic-upgrade  # Aplicar migrações
make seed-all        # Popular dados iniciais
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, leia nossas diretrizes de contribuição antes de submeter pull requests.

## 📄 Licença

Este projeto está licenciado sob a [Apache License 2.0](./LICENSE).

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!**
