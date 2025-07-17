# 🚀 Instruções para Build e Push das Imagens Docker

## 📋 Comandos para Executar

### 1. Tornar o script executável:
```bash
chmod +x build-and-push.sh
```

### 2. Executar o script de build e push:
```bash
./build-and-push.sh
```

## 🔧 Comandos Manuais (alternativa)

Se preferir executar manualmente:

### Build Backend:
```bash
docker build -t resper1965/gabi-agent-backend:latest .
```

### Build Frontend:
```bash
cd frontend
docker build -t resper1965/gabi-agent-frontend:latest .
cd ..
```

### Push para Docker Hub:
```bash
docker push resper1965/gabi-agent-backend:latest
docker push resper1965/gabi-agent-frontend:latest
```

## ⏱️ Tempo Estimado
- **Build Backend:** 5-10 minutos
- **Build Frontend:** 3-5 minutos  
- **Push:** 2-3 minutos por imagem

## ✅ Verificação
```bash
docker images | grep gabi-agent
```

## 📝 Após o Build
Execute o commit:
```bash
git add .
git commit -m "feat: atualizar imagens Docker com processo otimizado"
git push origin main
```

---

**Execute estes comandos no terminal para atualizar as imagens no Docker Hub!** 