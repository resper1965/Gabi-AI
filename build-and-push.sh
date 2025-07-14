#!/bin/bash

echo "🚀 Iniciando build e push das imagens Docker do Gabi Agent..."

# Verificar se estamos no diretório correto
if [ ! -f "Dockerfile" ]; then
    echo "❌ Erro: Execute este script no diretório gabi-agent"
    exit 1
fi

echo "📦 Build da imagem do Backend..."
docker build -t resper1965/gabi-agent-backend:latest .

if [ $? -eq 0 ]; then
    echo "✅ Backend buildado com sucesso!"
else
    echo "❌ Erro no build do Backend"
    exit 1
fi

echo "📦 Build da imagem do Frontend..."
cd frontend
docker build -t resper1965/gabi-agent-frontend:latest .

if [ $? -eq 0 ]; then
    echo "✅ Frontend buildado com sucesso!"
else
    echo "❌ Erro no build do Frontend"
    exit 1
fi

cd ..

echo "🚀 Push da imagem do Backend para Docker Hub..."
docker push resper1965/gabi-agent-backend:latest

if [ $? -eq 0 ]; then
    echo "✅ Backend enviado para Docker Hub!"
else
    echo "❌ Erro no push do Backend"
    exit 1
fi

echo "🚀 Push da imagem do Frontend para Docker Hub..."
docker push resper1965/gabi-agent-frontend:latest

if [ $? -eq 0 ]; then
    echo "✅ Frontend enviado para Docker Hub!"
else
    echo "❌ Erro no push do Frontend"
    exit 1
fi

echo "📋 Verificando imagens criadas..."
docker images | grep gabi-agent

echo "🎉 Build e push concluídos com sucesso!"
echo "📝 Imagens atualizadas no Docker Hub:"
echo "   - resper1965/gabi-agent-backend:latest"
echo "   - resper1965/gabi-agent-frontend:latest" 