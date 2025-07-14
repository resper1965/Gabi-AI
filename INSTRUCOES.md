# 🚀 Gabi AI - Instruções de Uso

## ✅ Clonagem Concluída!

Sua aplicação foi criada com sucesso em `/home/resper/gabi-ai/gabi-ai/` baseada no Evo AI e personalizada como Gabi AI.

## 📋 O que foi configurado

### ✅ Estrutura do Projeto
- **Backend**: FastAPI com todas as funcionalidades do Evo AI
- **Frontend**: Next.js 15 com interface moderna
- **Banco de Dados**: PostgreSQL configurado
- **Cache**: Redis configurado
- **Docker**: Configuração completa para desenvolvimento e produção

### ✅ Arquivos Criados/Modificados
- `pyproject.toml` - Configuração do projeto Python
- `package.json` - Configuração do frontend
- `README.md` - Documentação atualizada
- `DEVELOPMENT.md` - Guia de desenvolvimento
- `setup.sh` - Script de setup automático
- `docker-compose.yml` - Configuração Docker
- `nginx/nginx.conf` - Configuração do proxy reverso
- `Makefile` - Comandos úteis para desenvolvimento
- `.env.example` - Exemplo de variáveis de ambiente

## 🚀 Próximos Passos

### 1. Configurar Ambiente de Desenvolvimento

```bash
cd /home/resper/gabi-ai/gabi-ai

# Executar setup automático
./setup.sh
```

### 2. Configurar Variáveis de Ambiente

```bash
# Backend
cp .env.example .env
# Edite o arquivo .env com suas configurações

# Frontend
cd frontend
cp .env.example .env
# Edite o arquivo .env com a URL da API (http://localhost:8000)
cd ..
```

### 3. Configurar Banco de Dados

```bash
# Instalar PostgreSQL e Redis (se não estiverem instalados)
sudo apt install postgresql postgresql-contrib redis-server

# Criar banco de dados
sudo -u postgres createdb nova_aplicacao_db
sudo -u postgres createdb nova_aplicacao_test_db

# Aplicar migrações
make alembic-upgrade

# Criar dados iniciais
make seed-all
```

### 4. Iniciar a Aplicação

```bash
# Terminal 1 - Backend
make run

# Terminal 2 - Frontend
cd frontend
pnpm dev
```

## 🌐 URLs de Acesso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs
- **Admin do Banco**: http://localhost:8000/admin

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
make help              # Ver todos os comandos disponíveis
make run               # Iniciar backend em desenvolvimento
make run-prod          # Iniciar backend em produção
make test              # Executar testes
make lint              # Verificar código
make format            # Formatar código
```

### Banco de Dados
```bash
make alembic-upgrade   # Aplicar migrações
make alembic-revision message="descrição"  # Criar nova migração
make seed-all          # Criar dados iniciais
```

### Docker
```bash
make docker-build      # Construir imagens
make docker-run        # Executar com Docker
make docker-stop       # Parar containers
```

### Frontend
```bash
cd frontend
pnpm dev               # Desenvolvimento
pnpm build             # Build de produção
pnpm start             # Produção
```

## 🎯 Funcionalidades Disponíveis

### Backend (FastAPI)
- ✅ Autenticação JWT com verificação de email
- ✅ Gerenciamento de usuários e clientes
- ✅ Criação e execução de agentes de IA
- ✅ Integração com múltiplos modelos de IA
- ✅ Sistema de ferramentas personalizadas
- ✅ Protocolo A2A (Agent-to-Agent)
- ✅ Workflows com LangGraph
- ✅ Suporte a CrewAI
- ✅ Sistema de auditoria
- ✅ Email templates
- ✅ Rate limiting e segurança

### Frontend (Next.js)
- ✅ Interface moderna com Tailwind CSS
- ✅ Gerenciamento de agentes
- ✅ Chat em tempo real
- ✅ Workflows visuais
- ✅ Dashboard administrativo
- ✅ Sistema de autenticação
- ✅ Responsivo para mobile

## 🔒 Configurações de Segurança

### Variáveis Importantes no .env
```env
# Chaves obrigatórias
JWT_SECRET_KEY=sua-chave-super-secreta
DATABASE_URL=postgresql://user:password@localhost:5432/nova_aplicacao_db
REDIS_URL=redis://localhost:6379/0

# Chaves de API para IA
OPENAI_API_KEY=sua-chave-openai
ANTHROPIC_API_KEY=sua-chave-anthropic

# Email (opcional)
SENDGRID_API_KEY=sua-chave-sendgrid
```

## 📚 Documentação

- `README.md` - Visão geral do projeto
- `DEVELOPMENT.md` - Guia de desenvolvimento detalhado
- `http://localhost:8000/docs` - Documentação interativa da API

## 🐛 Solução de Problemas

### Problema: Erro de conexão com banco
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Iniciar se necessário
sudo systemctl start postgresql
```

### Problema: Erro de conexão com Redis
```bash
# Verificar se Redis está rodando
sudo systemctl status redis-server

# Iniciar se necessário
sudo systemctl start redis-server
```

### Problema: Dependências não encontradas
```bash
# Reinstalar dependências
make install-dev
cd frontend && pnpm install
```

## 🎉 Pronto para Desenvolver!

Sua nova aplicação está pronta para ser personalizada com suas funcionalidades específicas. Você pode:

1. **Modificar modelos** em `src/models/`
2. **Adicionar rotas** em `src/api/`
3. **Criar serviços** em `src/services/`
4. **Personalizar frontend** em `frontend/app/`
5. **Adicionar testes** em `tests/`

## 📞 Suporte

Se precisar de ajuda:
1. Consulte a documentação
2. Verifique os logs da aplicação
3. Execute `make help` para ver todos os comandos disponíveis

---

**Boa sorte com sua nova aplicação! 🚀** 