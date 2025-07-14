-- Script de inicialização do banco de dados para Nova Aplicação
-- Este script é executado automaticamente quando o container PostgreSQL é criado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Criar banco de dados de teste se não existir
SELECT 'CREATE DATABASE nova_aplicacao_test_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nova_aplicacao_test_db')\gexec

-- Conceder privilégios ao usuário
GRANT ALL PRIVILEGES ON DATABASE nova_aplicacao_db TO nova_user;
GRANT ALL PRIVILEGES ON DATABASE nova_aplicacao_test_db TO nova_user;

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
COMMENT ON DATABASE nova_aplicacao_db IS 'Banco de dados principal da Nova Aplicação';
COMMENT ON DATABASE nova_aplicacao_test_db IS 'Banco de dados de testes da Nova Aplicação'; 