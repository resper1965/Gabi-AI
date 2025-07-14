-- Script de inicialização do banco de dados para Gabi AI
-- Este script é executado automaticamente quando o container PostgreSQL é criado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Criar banco de dados de teste se não existir
SELECT 'CREATE DATABASE gabi_ai_test_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gabi_ai_test_db')\gexec

-- Conceder privilégios ao usuário
GRANT ALL PRIVILEGES ON DATABASE gabi_ai_db TO gabi_user;
GRANT ALL PRIVILEGES ON DATABASE gabi_ai_test_db TO gabi_user;

-- Configurar timezone
SET timezone = 'UTC';

-- Criar função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Comentário sobre o banco
COMMENT ON DATABASE gabi_ai_db IS 'Banco de dados principal do Gabi AI';
COMMENT ON DATABASE gabi_ai_test_db IS 'Banco de dados de testes do Gabi AI'; 