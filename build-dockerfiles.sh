#!/bin/bash

# Script para buildar as imagens Docker do Gabi AI Agent
set -e

echo "🚀 Iniciando build das imagens Docker..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Verificar se estamos no diretório correto
if [ ! -f "Dockerfile" ]; then
    error "Execute este script no diretório raiz do projeto (gabi-agent/)"
    exit 1
fi

# Build Backend
log "🔧 Buildando imagem do Backend..."
docker build -t resper1965/gabi-agent-backend:latest .
if [ $? -eq 0 ]; then
    success "Backend buildado com sucesso!"
else
    error "Falha no build do Backend"
    exit 1
fi

# Build Frontend
log "🎨 Buildando imagem do Frontend..."
cd frontend
docker build -t resper1965/gabi-agent-frontend:latest .
if [ $? -eq 0 ]; then
    success "Frontend buildado com sucesso!"
else
    error "Falha no build do Frontend"
    exit 1
fi
cd ..

# Push para Docker Hub
log "📤 Enviando imagens para Docker Hub..."

log "Enviando Backend..."
docker push resper1965/gabi-agent-backend:latest
if [ $? -eq 0 ]; then
    success "Backend enviado para Docker Hub!"
else
    error "Falha no push do Backend"
    exit 1
fi

log "Enviando Frontend..."
docker push resper1965/gabi-agent-frontend:latest
if [ $? -eq 0 ]; then
    success "Frontend enviado para Docker Hub!"
else
    error "Falha no push do Frontend"
    exit 1
fi

# Verificar imagens
log "🔍 Verificando imagens criadas..."
docker images | grep gabi-agent

success "✅ Build e push concluídos com sucesso!"
echo ""
echo "📋 Resumo:"
echo "   Backend:  resper1965/gabi-agent-backend:latest"
echo "   Frontend: resper1965/gabi-agent-frontend:latest"
echo ""
echo "🚀 Próximo passo: Deploy no EasyPanel!" 