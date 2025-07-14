#!/bin/bash

echo "🚀 Executando build, push e commit das imagens Docker..."

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

echo "📝 Fazendo commit das mudanças..."
git add .
git commit -m "feat: atualizar imagens Docker com processo otimizado para EasyPanel

- Atualizar backend com script de inicialização do banco
- Corrigir seeder do admin com suporte a múltiplas variáveis
- Otimizar processo de criação automática do banco gabi_ai_db
- Configurar credenciais padrão: resper@ness.com.br / admin123"

echo "🚀 Push para o repositório..."
git push origin main

echo "🎉 Processo completo finalizado!"
echo "📝 Imagens atualizadas no Docker Hub:"
echo "   - resper1965/gabi-agent-backend:latest"
echo "   - resper1965/gabi-agent-frontend:latest"
echo "📝 Código commitado e enviado para o GitHub" 