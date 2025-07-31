from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Jogo(BaseModel):
    id: int = Field(..., description="ID único do jogo")
    titulo: str = Field(..., max_length=100, description="Nome do jogo")
    genero: str = Field(..., max_length=50, description="Gênero do jogo")
    plataforma: str = Field(..., max_length=50, description="Plataforma do jogo")
    ano_lancamento: int = Field(..., ge=1950, le=datetime.now().year, description="Ano de lançamento")
    disponivel: bool = Field(default=True, description="Disponibilidade para empréstimo")

class Amigo(BaseModel):
    id: int = Field(..., description="ID único do amigo")
    nome: str = Field(..., max_length=100, description="Nome completo")
    telefone: str = Field(..., max_length=20, description="Número de telefone")
    email: Optional[str] = Field(None, max_length=100, description="Endereço de e-mail")
    data_cadastro: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), description="Data de cadastro")

class Emprestimo(BaseModel):
    id: int = Field(..., description="ID único do empréstimo")
    jogo_id: int = Field(..., description="ID do jogo emprestado")
    amigo_id: int = Field(..., description="ID do amigo que pegou emprestado")
    data_emprestimo: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), description="Data do empréstimo")
    data_devolucao: str = Field(..., description="Data prevista para devolução")