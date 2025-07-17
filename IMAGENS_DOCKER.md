# Imagens Docker para Deploy no EasyPanel

## Backend (API Service)
- **Imagem:** `resper1965/gabi-agent-backend:latest`
- **Porta:** 8000

## Frontend
- **Imagem:** `resper1965/gabi-agent-frontend:latest`
- **Porta:** 3000

## Como usar no EasyPanel

1. **No painel do EasyPanel**, ao criar um novo serviço do tipo "App":
   - Para o backend, use a imagem `resper1965/gabi-agent-backend:latest` e configure a porta 8000.
   - Para o frontend, use a imagem `resper1965/gabi-agent-frontend:latest` e configure a porta 3000.

2. **Configure as variáveis de ambiente** conforme a documentação do projeto (veja `INSTALACAO_EASYPANEL.md`).

3. **Exemplo de configuração manual:**

```
Backend:
  Image: resper1965/gabi-agent-backend:latest
  Port: 8000

Frontend:
  Image: resper1965/gabi-agent-frontend:latest
  Port: 3000
```

Essas imagens já estão prontas para uso e compatíveis com o EasyPanel. 