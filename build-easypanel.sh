#!/bin/bash

# Script para build das imagens Docker do Gabi Agent para EasyPanel
# Autor: resper1965
# Data: 2025-01-14

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    error "Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    error "Execute este script no diretório raiz do projeto (onde está o pyproject.toml)"
    exit 1
fi

# Configurações
BACKEND_IMAGE="resper1965/gabi-agent-backend"
FRONTEND_IMAGE="resper1965/gabi-agent-frontend"
VERSION=${1:-latest}

log "🚀 Iniciando build das imagens Docker para EasyPanel"
log "Versão: $VERSION"

# Build da imagem do Backend
log "📦 Buildando imagem do Backend..."
docker build -t $BACKEND_IMAGE:$VERSION -t $BACKEND_IMAGE:latest .

if [ $? -eq 0 ]; then
    log "✅ Backend buildado com sucesso!"
else
    error "❌ Falha no build do Backend"
    exit 1
fi

# Build da imagem do Frontend
log "📦 Buildando imagem do Frontend..."
docker build -t $FRONTEND_IMAGE:$VERSION -t $FRONTEND_IMAGE:latest ./frontend

if [ $? -eq 0 ]; then
    log "✅ Frontend buildado com sucesso!"
else
    error "❌ Falha no build do Frontend"
    exit 1
fi

# Perguntar se quer fazer push para o Docker Hub
read -p "🤔 Deseja fazer push das imagens para o Docker Hub? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "📤 Fazendo push das imagens para o Docker Hub..."
    
    # Push do Backend
    log "📤 Push da imagem do Backend..."
    docker push $BACKEND_IMAGE:$VERSION
    docker push $BACKEND_IMAGE:latest
    
    # Push do Frontend
    log "📤 Push da imagem do Frontend..."
    docker push $FRONTEND_IMAGE:$VERSION
    docker push $FRONTEND_IMAGE:latest
    
    log "✅ Push concluído com sucesso!"
fi

# Mostrar informações das imagens
log "📊 Informações das imagens criadas:"
echo
echo "Backend:"
echo "  - $BACKEND_IMAGE:$VERSION"
echo "  - $BACKEND_IMAGE:latest"
echo
echo "Frontend:"
echo "  - $FRONTEND_IMAGE:$VERSION"
echo "  - $FRONTEND_IMAGE:latest"
echo

# Mostrar comandos para uso no EasyPanel
log "🎯 Para usar no EasyPanel:"
echo
echo "1. Use o arquivo 'easypanel-install.json' para instalação automática"
echo "2. Ou configure manualmente com as seguintes imagens:"
echo
echo "Backend:"
echo "  Image: $BACKEND_IMAGE:latest"
echo "  Port: 8000"
echo
echo "Frontend:"
echo "  Image: $FRONTEND_IMAGE:latest"
echo "  Port: 3000"
echo

log "🎉 Build concluído com sucesso!"
log "📚 Consulte o arquivo INSTALACAO_EASYPANEL.md para instruções detalhadas" 