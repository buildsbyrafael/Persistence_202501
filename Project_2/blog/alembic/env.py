import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Adiciona o caminho raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as configurações e os modelos
from core.config import settings
from models import *  # Importa todos os modelos
from sqlmodel import SQLModel

# Configuração do arquivo .ini do Alembic
config = context.config
fileConfig(config.config_file_name)

# Define a URL do banco de dados a partir das configurações
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadata dos modelos (necessário para autogenerate)
target_metadata = SQLModel.metadata

# Substitui AutoString por String nas migrações automaticamente
def render_item(type_, obj, autogen_context):
    """Substitui AutoString por sa.String() nas migrações."""
    if type_ == "type" and obj.__class__.__name__ == "AutoString":
        autogen_context.imports.add("import sqlalchemy as sa")
        return "sa.String()"
    return False

def run_migrations_offline():
    """Executa migrações no modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Executa migrações no modo online."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()