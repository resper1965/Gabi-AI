# Guia de Desenvolvimento - Nova Aplicação

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- pnpm (recomendado) ou npm/yarn

### Setup Inicial

1. **Clone o repositório**
   ```bash
   git clone <seu-repositorio>
   cd nova-aplicacao
   ```

2. **Execute o script de setup**
   ```bash
   ./setup.sh
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   # Backend
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   
   # Frontend
   cd frontend
   cp .env.example .env
   # Edite o arquivo .env com a URL da API
   cd ..
   ```

4. **Configure o banco de dados**
   ```bash
   make alembic-upgrade
   make seed-all
   ```

5. **Inicie a aplicação**
   ```bash
   # Terminal 1 - Backend
   make run
   
   # Terminal 2 - Frontend
   cd frontend
   pnpm dev
   ```

## 🏗️ Estrutura do Projeto

### Backend (FastAPI)
```
src/
├── api/                 # Rotas da API
├── config/              # Configurações
├── core/                # Middleware e componentes centrais
├── models/              # Modelos SQLAlchemy
├── schemas/             # Schemas Pydantic
├── services/            # Lógica de negócio
├── templates/           # Templates de email
└── utils/               # Utilitários
```

### Frontend (Next.js)
```
frontend/
├── app/                 # Páginas e rotas (App Router)
├── components/          # Componentes React
├── contexts/            # Contextos React
├── hooks/               # Custom hooks
├── lib/                 # Utilitários e configurações
├── services/            # Serviços de API
├── styles/              # Estilos globais
└── types/               # Definições TypeScript
```

## 🛠️ Comandos Úteis

### Backend
```bash
# Desenvolvimento
make run                 # Iniciar servidor de desenvolvimento
make run-prod            # Iniciar servidor de produção

# Banco de dados
make alembic-revision message="descrição"  # Criar nova migração
make alembic-upgrade                       # Aplicar migrações
make alembic-downgrade                     # Reverter última migração
make alembic-reset                         # Resetar banco

# Qualidade de código
make lint                 # Executar linting
make format               # Formatar código
make test                 # Executar testes

# Instalação
make install              # Instalar dependências
make install-dev          # Instalar dependências de desenvolvimento
```

### Frontend
```bash
cd frontend

# Desenvolvimento
pnpm dev                  # Iniciar servidor de desenvolvimento
pnpm build                # Build de produção
pnpm start                # Iniciar servidor de produção

# Qualidade de código
pnpm lint                 # Executar linting
pnpm type-check           # Verificar tipos TypeScript
```

## 🔧 Configuração de Desenvolvimento

### Variáveis de Ambiente

#### Backend (.env)
```env
# Configurações essenciais
DATABASE_URL=postgresql://user:password@localhost:5432/nova_aplicacao_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key

# Email (opcional para desenvolvimento)
SENDGRID_API_KEY=your-sendgrid-key
# ou
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Chaves de API para IA
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

#### Frontend (frontend/.env)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Nova Aplicação
```

### Banco de Dados

1. **Instalar PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   ```

2. **Criar banco de dados**
   ```bash
   sudo -u postgres createdb nova_aplicacao_db
   sudo -u postgres createdb nova_aplicacao_test_db
   ```

3. **Configurar usuário**
   ```bash
   sudo -u postgres psql
   CREATE USER nova_user WITH PASSWORD 'nova_password';
   GRANT ALL PRIVILEGES ON DATABASE nova_aplicacao_db TO nova_user;
   GRANT ALL PRIVILEGES ON DATABASE nova_aplicacao_test_db TO nova_user;
   \q
   ```

### Redis

```bash
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Iniciar serviço
sudo systemctl start redis-server  # Linux
brew services start redis          # macOS
```

## 🧪 Testes

### Backend
```bash
# Executar todos os testes
make test

# Executar testes com coverage
pytest --cov=src tests/

# Executar testes específicos
pytest tests/api/test_auth_routes.py
```

### Frontend
```bash
cd frontend

# Executar testes
pnpm test

# Executar testes em modo watch
pnpm test:watch
```

## 📦 Deploy

### Docker
```bash
# Build da aplicação
make docker-build

# Executar com Docker Compose
docker-compose up -d
```

### Produção
```bash
# Backend
make run-prod

# Frontend
cd frontend
pnpm build
pnpm start
```

## 🔍 Debugging

### Backend
```bash
# Logs detalhados
LOG_LEVEL=DEBUG make run

# Debug com pdb
python -m pdb -m uvicorn src.main:app --reload
```

### Frontend
```bash
# Modo debug
NEXT_PUBLIC_DEBUG_MODE=true pnpm dev
```

## 📚 Recursos Adicionais

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação Next.js](https://nextjs.org/docs)
- [Documentação SQLAlchemy](https://docs.sqlalchemy.org/)
- [Documentação Pydantic](https://docs.pydantic.dev/)
- [Documentação Tailwind CSS](https://tailwindcss.com/docs)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Padrões de Código

### Python
- Use Black para formatação
- Use Flake8 para linting
- Siga PEP 8
- Documente funções e classes
- Use type hints

### TypeScript/JavaScript
- Use ESLint e Prettier
- Siga as convenções do Next.js
- Use TypeScript strict mode
- Documente componentes e funções

### Git
- Use Conventional Commits
- Faça commits pequenos e focados
- Escreva mensagens claras e descritivas 