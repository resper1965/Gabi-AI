# Makefile para Nova Aplicação
# Baseado no Evo AI

.PHONY: help install install-dev run run-prod test lint format clean venv docker-build docker-run docker-stop

# Variáveis
PYTHON = python3
PIP = pip
PYTEST = pytest
BLACK = black
FLAKE8 = flake8
UVICORN = uvicorn
ALEMBIC = alembic

# Configurações
APP_NAME = nova-aplicacao
APP_MODULE = src.main:app
HOST = 0.0.0.0
PORT = 8000
WORKERS = 4

# Cores para output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Mostrar esta ajuda
	@echo "$(BLUE)Nova Aplicação - Comandos Disponíveis$(NC)"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instalar dependências do projeto
	@echo "$(BLUE)Instalando dependências...$(NC)"
	$(PIP) install -e .

install-dev: ## Instalar dependências de desenvolvimento
	@echo "$(BLUE)Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install -e ".[dev]"

venv: ## Criar ambiente virtual
	@echo "$(BLUE)Criando ambiente virtual...$(NC)"
	$(PYTHON) -m venv venv
	@echo "$(GREEN)Ambiente virtual criado!$(NC)"
	@echo "$(YELLOW)Para ativar: source venv/bin/activate$(NC)"

run: ## Executar aplicação em modo desenvolvimento
	@echo "$(BLUE)Iniciando servidor de desenvolvimento...$(NC)"
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

run-prod: ## Executar aplicação em modo produção
	@echo "$(BLUE)Iniciando servidor de produção...$(NC)"
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --workers $(WORKERS)

test: ## Executar testes
	@echo "$(BLUE)Executando testes...$(NC)"
	$(PYTEST) tests/ -v

test-cov: ## Executar testes com coverage
	@echo "$(BLUE)Executando testes com coverage...$(NC)"
	$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Executar linting
	@echo "$(BLUE)Executando linting...$(NC)"
	$(FLAKE8) src/ tests/

format: ## Formatar código
	@echo "$(BLUE)Formatando código...$(NC)"
	$(BLACK) src/ tests/

format-check: ## Verificar formatação do código
	@echo "$(BLUE)Verificando formatação...$(NC)"
	$(BLACK) --check src/ tests/

clean: ## Limpar cache e arquivos temporários
	@echo "$(BLUE)Limpando cache...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	rm -rf htmlcov/
	@echo "$(GREEN)Cache limpo!$(NC)"

# Comandos do Alembic
alembic-revision: ## Criar nova migração (use: make alembic-revision message="descrição")
	@echo "$(BLUE)Criando nova migração...$(NC)"
	$(ALEMBIC) revision --autogenerate -m "$(message)"

alembic-upgrade: ## Aplicar migrações pendentes
	@echo "$(BLUE)Aplicando migrações...$(NC)"
	$(ALEMBIC) upgrade head

alembic-downgrade: ## Reverter última migração
	@echo "$(BLUE)Revertendo última migração...$(NC)"
	$(ALEMBIC) downgrade -1

alembic-migrate: ## Criar e aplicar nova migração (use: make alembic-migrate message="descrição")
	@echo "$(BLUE)Criando e aplicando migração...$(NC)"
	$(ALEMBIC) revision --autogenerate -m "$(message)"
	$(ALEMBIC) upgrade head

alembic-reset: ## Resetar banco de dados
	@echo "$(YELLOW)⚠️  ATENÇÃO: Isso irá apagar todos os dados!$(NC)"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Resetando banco de dados...$(NC)"
	$(ALEMBIC) downgrade base
	$(ALEMBIC) upgrade head

alembic-upgrade-cascade: ## Forçar upgrade removendo dependências
	@echo "$(YELLOW)⚠️  ATENÇÃO: Isso pode causar perda de dados!$(NC)"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Forçando upgrade...$(NC)"
	$(ALEMBIC) upgrade head --sql

# Comandos de seed
seed-all: ## Executar todos os seeders
	@echo "$(BLUE)Executando seeders...$(NC)"
	$(PYTHON) -m scripts.seed_all

# Comandos Docker
docker-build: ## Build da aplicação com Docker
	@echo "$(BLUE)Construindo imagem Docker...$(NC)"
	docker-compose build

docker-run: ## Executar aplicação com Docker Compose
	@echo "$(BLUE)Iniciando aplicação com Docker...$(NC)"
	docker-compose up -d

docker-stop: ## Parar aplicação Docker
	@echo "$(BLUE)Parando aplicação Docker...$(NC)"
	docker-compose down

docker-logs: ## Ver logs da aplicação Docker
	@echo "$(BLUE)Mostrando logs...$(NC)"
	docker-compose logs -f

docker-clean: ## Limpar containers e volumes Docker
	@echo "$(YELLOW)⚠️  ATENÇÃO: Isso irá remover todos os containers e volumes!$(NC)"
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(BLUE)Limpando Docker...$(NC)"
	docker-compose down -v --remove-orphans
	docker system prune -f

# Comandos de desenvolvimento
dev-setup: ## Setup completo para desenvolvimento
	@echo "$(BLUE)Configurando ambiente de desenvolvimento...$(NC)"
	@if [ ! -d "venv" ]; then make venv; fi
	@echo "$(YELLOW)Ative o ambiente virtual: source venv/bin/activate$(NC)"
	@echo "$(YELLOW)Depois execute: make install-dev$(NC)"

check-deps: ## Verificar dependências
	@echo "$(BLUE)Verificando dependências...$(NC)"
	$(PIP) list --outdated

update-deps: ## Atualizar dependências
	@echo "$(BLUE)Atualizando dependências...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[dev]"

# Comandos de segurança
security-check: ## Verificar vulnerabilidades de segurança
	@echo "$(BLUE)Verificando vulnerabilidades...$(NC)"
	$(PIP) install safety
	safety check

# Comandos de documentação
docs-serve: ## Servir documentação da API
	@echo "$(BLUE)Servindo documentação...$(NC)"
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --reload
	@echo "$(GREEN)Documentação disponível em: http://$(HOST):$(PORT)/docs$(NC)"

# Comandos de monitoramento
health-check: ## Verificar saúde da aplicação
	@echo "$(BLUE)Verificando saúde da aplicação...$(NC)"
	curl -f http://$(HOST):$(PORT)/health || echo "$(RED)Aplicação não está respondendo$(NC)"

# Comandos de backup
backup-db: ## Fazer backup do banco de dados
	@echo "$(BLUE)Fazendo backup do banco...$(NC)"
	@if [ -z "$(DB_NAME)" ]; then echo "$(RED)Defina DB_NAME=seu_banco$(NC)"; exit 1; fi
	pg_dump $(DB_NAME) > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup criado!$(NC)"

# Comandos de produção
prod-setup: ## Setup para produção
	@echo "$(BLUE)Configurando para produção...$(NC)"
	@echo "$(YELLOW)1. Configure as variáveis de ambiente$(NC)"
	@echo "$(YELLOW)2. Execute: make alembic-upgrade$(NC)"
	@echo "$(YELLOW)3. Execute: make run-prod$(NC)"

# Comandos de frontend
frontend-install: ## Instalar dependências do frontend
	@echo "$(BLUE)Instalando dependências do frontend...$(NC)"
	cd frontend && pnpm install

frontend-dev: ## Executar frontend em modo desenvolvimento
	@echo "$(BLUE)Iniciando frontend...$(NC)"
	cd frontend && pnpm dev

frontend-build: ## Build do frontend
	@echo "$(BLUE)Construindo frontend...$(NC)"
	cd frontend && pnpm build

frontend-start: ## Executar frontend em modo produção
	@echo "$(BLUE)Iniciando frontend em produção...$(NC)"
	cd frontend && pnpm start

# Comandos de deploy
deploy-staging: ## Deploy para staging
	@echo "$(BLUE)Deploy para staging...$(NC)"
	@echo "$(YELLOW)Implemente seu processo de deploy aqui$(NC)"

deploy-prod: ## Deploy para produção
	@echo "$(BLUE)Deploy para produção...$(NC)"
	@echo "$(YELLOW)Implemente seu processo de deploy aqui$(NC)"