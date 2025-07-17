# 🚀 EXECUTAR NO WSL - Build e Push das Imagens

## 📋 Comandos para executar no TERMINAL WSL:

### 1. Abrir o terminal WSL:
- Pressione `Windows + R`
- Digite `wsl` e pressione Enter
- Ou abra o "Ubuntu" no menu iniciar

### 2. Navegar para o diretório:
```bash
cd /home/resper/gabi-ai/gabi-agent
```

### 3. Verificar se está no lugar certo:
```bash
pwd
ls -la
```
Deve mostrar o Dockerfile e outros arquivos.

### 4. Tornar o script executável:
```bash
chmod +x EXECUTAR_BUILD.sh
```

### 5. Executar o build completo:
```bash
./EXECUTAR_BUILD.sh
```

## ⏱️ Tempo estimado: 15-20 minutos

## ✅ O que será feito:
1. Build da imagem do Backend
2. Build da imagem do Frontend
3. Push das imagens para Docker Hub
4. Commit e push para GitHub

## 🐛 Se der erro de permissão:
```bash
sudo chmod +x EXECUTAR_BUILD.sh
```

## 🐛 Se der erro de Docker:
```bash
sudo service docker start
```

---

**Execute no terminal WSL agora!** 🚀 