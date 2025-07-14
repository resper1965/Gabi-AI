#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do Gabi AI
Cria o banco se não existir e executa as migrações
"""

import os
import sys
import logging
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """Cria o banco de dados se não existir"""
    try:
        load_dotenv()
        
        # Get database connection string
        db_url = os.getenv("POSTGRES_CONNECTION_STRING") or os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("DATABASE_URL or POSTGRES_CONNECTION_STRING not found")
            return False
            
        # Parse connection string to get components
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # Extract components
        auth_part, rest = db_url.split("@", 1)
        user, password = auth_part.split(":", 1)
        host_port, database = rest.split("/", 1)
        host, port = host_port.split(":", 1) if ":" in host_port else (host_port, "5432")
        
        logger.info(f"Connecting to PostgreSQL at {host}:{port}")
        
        # Connect to default postgres database to create our database
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database: {database}")
            cursor.execute(f"CREATE DATABASE {database}")
            logger.info(f"Database {database} created successfully")
        else:
            logger.info(f"Database {database} already exists")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False


def run_migrations():
    """Executa as migrações do Alembic"""
    try:
        logger.info("Running database migrations...")
        os.system("alembic upgrade head")
        logger.info("Migrations completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error running migrations: {str(e)}")
        return False


def main():
    """Função principal"""
    logger.info("Starting database initialization...")
    
    # Create database if not exists
    if not create_database_if_not_exists():
        logger.error("Failed to create database")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        logger.error("Failed to run migrations")
        sys.exit(1)
    
    logger.info("Database initialization completed successfully")


if __name__ == "__main__":
    main() 