from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import create_db_and_tables
from core.config import settings
from core.logging_config import setup_logging

from routers import (
    user_router,
    post_router,
    comment_router,
    category_router,
    like_router
)

# Setup dos logs
setup_logging()

app = FastAPI(
    title="Blog Pessoal API",
    description="API RESTful para gestão completa de um blog pessoal.",
    version="1.0.0"
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Cria as tabelas no banco, caso não existam
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Incluindo os routers
routers = [
    user_router,
    post_router,
    comment_router,
    category_router,
    like_router
]

for router in routers:
    app.include_router(router)

# Rota raiz (opcional)
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "API está rodando. Acesse /docs para ver a documentação."
    }