#!/bin/sh
set -e

# Diretório onde o arquivo __ENV.js será gerado
ENV_FILE=/app/public/__ENV.js

# Gerar arquivo __ENV.js com as variáveis de ambiente atuais
echo "window.__ENV = {" > $ENV_FILE
env | grep "^NEXT_PUBLIC_" | while read -r line; do
  # Extrair nome e valor da variável
  key=$(echo "$line" | cut -d '=' -f 1)
  value=$(echo "$line" | cut -d '=' -f 2-)
  
  # Adicionar a variável ao arquivo __ENV.js
  echo "  \"$key\": \"$value\"," >> $ENV_FILE
done
echo "};" >> $ENV_FILE

# Iniciar a aplicação
exec pnpm start 