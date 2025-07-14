# 🚀 Instalação do Gabi Agent no EasyPanel

Este guia explica como instalar o Gabi Agent no EasyPanel de forma simples e rápida.

## 📋 Pré-requisitos

- EasyPanel instalado e configurado
- Acesso ao painel administrativo do EasyPanel
- Domínio configurado (opcional, mas recomendado)

## 🎯 Método 1: Instalação via Template (Recomendado)

### Passo 1: Acesse o EasyPanel
1. Faça login no seu painel EasyPanel
2. Vá para a seção "Templates" ou "Marketplace"

### Passo 2: Procure pelo Template
1. Procure por "Gabi Agent" na lista de templates
2. Clique em "Instalar" ou "Deploy"

### Passo 3: Configure as Variáveis
Configure as seguintes variáveis de ambiente:

#### Variáveis Obrigatórias:
- **POSTGRES_PASSWORD**: Senha do banco de dados (ex: `gabi_password_2024_segura`)
- **JWT_SECRET_KEY**: Chave secreta JWT (ex: `sua-chave-secreta-muito-segura`)
- **ADMIN_EMAIL**: Email do administrador (ex: `resper@ness.com.br`)
- **ADMIN_PASSWORD**: Senha do administrador (ex: `admin123`)

#### Variáveis de Domínio:
- **BACKEND_DOMAIN**: Domínio para o backend (ex: `api.your-domain.com`)
- **FRONTEND_DOMAIN**: Domínio para o frontend (ex: `your-domain.com`)
- **NEXT_PUBLIC_API_URL**: URL completa da API (ex: `https://api.your-domain.com`)

#### Variáveis Opcionais:
- **SENDGRID_API_KEY**: Chave API do SendGrid (para emails)
- **OPENAI_API_KEY**: Chave API da OpenAI
- **ANTHROPIC_API_KEY**: Chave API da Anthropic

### Passo 4: Deploy
1. Clique em "Deploy" ou "Instalar"
2. Aguarde a instalação completa
3. Acesse a aplicação no domínio configurado

## 🔧 Método 2: Instalação Manual via JSON

### Passo 1: Prepare o JSON
1. Copie o conteúdo do arquivo `easypanel-install.json`
2. Ajuste as variáveis conforme necessário

### Passo 2: Importe no EasyPanel
1. Vá para "Projects" no EasyPanel
2. Clique em "Create Project"
3. Selecione "Import from JSON"
4. Cole o JSON e configure as variáveis

## 🌐 Configuração de Domínios

### Para Produção:
```
BACKEND_DOMAIN=api.your-domain.com
FRONTEND_DOMAIN=your-domain.com
NEXT_PUBLIC_API_URL=https://api.your-domain.com
CORS_ORIGINS=https://your-domain.com
```

### Para Desenvolvimento:
```
BACKEND_DOMAIN=localhost
FRONTEND_DOMAIN=localhost
NEXT_PUBLIC_API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
```

## 🔐 Configuração de Segurança

### Senhas Recomendadas:
- **POSTGRES_PASSWORD**: Use uma senha forte (mínimo 12 caracteres)
- **JWT_SECRET_KEY**: Gere uma chave aleatória de 32+ caracteres
- **ADMIN_PASSWORD**: Use uma senha forte para o admin

### Exemplo de Senhas Seguras:
```bash
POSTGRES_PASSWORD=gabi_2024_super_segura_123!
JWT_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
ADMIN_PASSWORD=Admin@2024#Seguro!
```

## 🎯 Primeiro Acesso

1. **Acesse a aplicação**: `https://your-domain.com` ou `http://localhost:3000`
2. **Faça login com**:
   - **Email**: `resper@ness.com.br` (ou o email configurado)
   - **Senha**: `admin123` (ou a senha configurada)
3. **Configure**: MCP servers, clientes e agentes
4. **Teste**: Use o chat para interagir com seus agentes

## 📊 Verificação da Instalação

### Verificar Serviços:
- ✅ PostgreSQL: Banco de dados rodando
- ✅ Redis: Cache funcionando
- ✅ Backend: API disponível em `/docs`
- ✅ Frontend: Interface web acessível

### Verificar Logs:
```bash
# No EasyPanel, vá para cada serviço e verifique os logs
# Procure por mensagens de sucesso como:
# - "Admin created successfully"
# - "All seeders were executed successfully"
# - "Uvicorn running on http://0.0.0.0:8000"
```

## 🛠️ Solução de Problemas

### Problema: Erro de Conexão com Banco
**Solução**: Verifique se a variável `POSTGRES_PASSWORD` está correta

### Problema: Erro de Autenticação
**Solução**: Verifique se `ADMIN_EMAIL` e `ADMIN_PASSWORD` estão configurados

### Problema: Frontend não carrega
**Solução**: Verifique se `NEXT_PUBLIC_API_URL` está apontando para o backend correto

### Problema: CORS Error
**Solução**: Configure `CORS_ORIGINS` com o domínio correto

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs de cada serviço no EasyPanel
2. Confirme se todas as variáveis estão configuradas
3. Verifique se os domínios estão apontando corretamente
4. Consulte a documentação completa no README.md

## 🎉 Próximos Passos

Após a instalação bem-sucedida:
1. Configure MCP servers para funcionalidades avançadas
2. Adicione suas chaves de API (OpenAI, Anthropic, etc.)
3. Configure o SendGrid para envio de emails
4. Personalize a interface conforme necessário
5. Configure backups do banco de dados

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!** 