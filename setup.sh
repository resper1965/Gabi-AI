#!/bin/bash

# Script de Setup para Nova Aplicação
# Baseado no Evo AI

set -e

echo "🚀 Configurando Nova Aplicação..."
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Python 3.10+ está instalado
print_status "Verificando versão do Python..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    print_success "Python $python_version encontrado (>= $required_version)"
else
    print_error "Python 3.10+ é necessário. Versão atual: $python_version"
    exit 1
fi

# Verificar se Node.js 18+ está instalado
print_status "Verificando versão do Node.js..."
if command -v node &> /dev/null; then
    node_version=$(node --version | cut -d'v' -f2 | cut -d. -f1)
    if [ "$node_version" -ge 18 ]; then
        print_success "Node.js $(node --version) encontrado (>= 18)"
    else
        print_error "Node.js 18+ é necessário. Versão atual: $(node --version)"
        exit 1
    fi
else
    print_error "Node.js não encontrado. Instale Node.js 18+"
    exit 1
fi

# Verificar se pnpm está instalado
print_status "Verificando pnpm..."
if command -v pnpm &> /dev/null; then
    print_success "pnpm encontrado"
else
    print_warning "pnpm não encontrado. Instalando..."
    npm install -g pnpm
    print_success "pnpm instalado"
fi

# Criar ambiente virtual Python
print_status "Criando ambiente virtual Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Ambiente virtual criado"
else
    print_warning "Ambiente virtual já existe"
fi

# Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências Python
print_status "Instalando dependências Python..."
pip install --upgrade pip
pip install -e ".[dev]"

# Configurar arquivo de ambiente
print_status "Configurando arquivo de ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Arquivo .env criado. Configure as variáveis de ambiente!"
else
    print_warning "Arquivo .env já existe"
fi

# Configurar frontend
print_status "Configurando frontend..."
cd frontend

# Instalar dependências do frontend
print_status "Instalando dependências do frontend..."
pnpm install

# Configurar arquivo de ambiente do frontend
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_warning "Arquivo .env do frontend criado. Configure as variáveis!"
else
    print_warning "Arquivo .env do frontend já existe"
fi

cd ..

# Verificar se PostgreSQL está rodando
print_status "Verificando PostgreSQL..."
if command -v pg_isready &> /dev/null; then
    if pg_isready -q; then
        print_success "PostgreSQL está rodando"
    else
        print_warning "PostgreSQL não está rodando. Inicie o serviço PostgreSQL"
    fi
else
    print_warning "PostgreSQL não encontrado. Instale PostgreSQL 13+"
fi

# Verificar se Redis está rodando
print_status "Verificando Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_success "Redis está rodando"
    else
        print_warning "Redis não está rodando. Inicie o serviço Redis"
    fi
else
    print_warning "Redis não encontrado. Instale Redis 6+"
fi

echo ""
echo "🎉 Setup concluído!"
echo "=================="
echo ""
echo "Próximos passos:"
echo "1. Configure o arquivo .env com suas credenciais"
echo "2. Configure o arquivo frontend/.env com a URL da API"
echo "3. Inicie o PostgreSQL e Redis"
echo "4. Execute: make alembic-upgrade (para configurar o banco)"
echo "5. Execute: make seed-all (para criar dados iniciais)"
echo "6. Execute: make run (para iniciar o backend)"
echo "7. Execute: cd frontend && pnpm dev (para iniciar o frontend)"
echo ""
echo "📚 Documentação: README.md"
echo "🐛 Problemas: Verifique os logs ou consulte a documentação"
echo "" 