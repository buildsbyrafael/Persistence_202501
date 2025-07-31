from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import RedirectResponse, FileResponse
from models import Jogo, Amigo, Emprestimo
from database import (
    carregar_jogos, criar_jogo as criar_jogo_db, atualizar_jogo as atualizar_jogo_db, deletar_jogo,
    carregar_amigos, criar_amigo as criar_amigo_db, atualizar_amigo as atualizar_amigo_db, deletar_amigo,
    carregar_emprestimos, criar_emprestimo as criar_emprestimo_db, 
    atualizar_emprestimo as atualizar_emprestimo_db, deletar_emprestimo,
    contar_entidades, compactar_csv_para_zip, calcular_hash_csv, converter_csv_para_xml
)
import logging
from typing import List, Optional
from pathlib import Path

app = FastAPI(title="API de Gerenciamento de Jogos", version="2.1")

# Configuração de logs
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    filename="logs/api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="a"
)

@app.get("/")
async def root():
    """Redireciona para a documentação Swagger UI"""
    return RedirectResponse(url="/docs")

# ========== Endpoints para Jogos ==========
@app.post("/jogos/", response_model=Jogo, status_code=status.HTTP_201_CREATED)
async def criar_jogo(jogo: Jogo):
    """Cria um novo jogo"""
    try:
        jogo_criado = criar_jogo_db(jogo)
        logging.info(f"Jogo criado | ID: {jogo.id} | Nome: {jogo.titulo}")
        return jogo_criado
    except ValueError as e:
        logging.error(f"Erro ao criar jogo: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/jogos/", response_model=List[Jogo])
async def listar_jogos():
    """Lista todos os jogos cadastrados"""
    return carregar_jogos()

@app.get("/jogos/{jogo_id}", response_model=Jogo)
async def obter_jogo(jogo_id: int):
    """Obtém um jogo específico pelo ID"""
    jogo = next((j for j in carregar_jogos() if j.id == jogo_id), None)
    if not jogo:
        logging.warning(f"Jogo não encontrado | ID: {jogo_id}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Jogo com ID {jogo_id} não encontrado")
    return jogo

@app.put("/jogos/{jogo_id}", response_model=Jogo)
async def atualizar_jogo(jogo_id: int, jogo: Jogo):
    """Atualiza um jogo existente"""
    try:
        jogo_atualizado = atualizar_jogo_db(jogo_id, jogo)
        if jogo_atualizado is None:
            logging.warning(f"Jogo não encontrado para atualização | ID: {jogo_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Jogo com ID {jogo_id} não encontrado")
        logging.info(f"Jogo atualizado | ID Antigo: {jogo_id} | Novo ID: {jogo.id}")
        return jogo_atualizado
    except ValueError as e:
        logging.error(f"Erro ao atualizar jogo: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/jogos/{jogo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_jogo(jogo_id: int):
    """Remove um jogo pelo ID"""
    if not deletar_jogo(jogo_id):
        logging.warning(f"Tentativa de excluir jogo não encontrado | ID: {jogo_id}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Jogo com ID {jogo_id} não encontrado")
    logging.info(f"Jogo excluído | ID: {jogo_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/jogos/contagem/")
async def contar_jogos():
    """Retorna a quantidade de jogos cadastrados"""
    return {"quantidade": contar_entidades("jogos")}

@app.get("/jogos/filtrar/")
async def filtrar_jogos(
    genero: Optional[str] = None,
    plataforma: Optional[str] = None,
    disponivel: Optional[bool] = None,
    ano_min: Optional[int] = None,
    ano_max: Optional[int] = None
):
    """Filtra jogos por parâmetros"""
    jogos = carregar_jogos()
    
    if genero:
        jogos = [j for j in jogos if j.genero.lower() == genero.lower()]
    if plataforma:
        jogos = [j for j in jogos if j.plataforma.lower() == plataforma.lower()]
    if disponivel is not None:
        jogos = [j for j in jogos if j.disponivel == disponivel]
    if ano_min:
        jogos = [j for j in jogos if j.ano_lancamento >= ano_min]
    if ano_max:
        jogos = [j for j in jogos if j.ano_lancamento <= ano_max]
    
    logging.info(f"Filtro aplicado | Jogos encontrados: {len(jogos)}")
    return jogos

@app.get("/jogos/zip/")
async def download_zip_jogos():
    """Gera e disponibiliza download do arquivo ZIP com jogos"""
    zip_path = compactar_csv_para_zip("jogos")
    logging.info("Arquivo ZIP de jogos gerado com sucesso")
    return FileResponse(zip_path, filename="jogos.zip")

@app.get("/jogos/hash/")
async def hash_jogos():
    """Retorna hash SHA256 do arquivo de jogos"""
    hash_value = calcular_hash_csv("jogos")
    logging.info(f"Hash SHA256 calculado para jogos: {hash_value}")
    return {"hash_sha256": hash_value}

@app.get("/jogos/xml/")
async def xml_jogos():
    """Converte e disponibiliza dados dos jogos em XML"""
    xml_path = converter_csv_para_xml("jogos")
    logging.info("Arquivo XML de jogos gerado com sucesso")
    return FileResponse(xml_path, filename="jogos.xml")

# ========== Endpoints para Amigos ==========
@app.post("/amigos/", response_model=Amigo, status_code=status.HTTP_201_CREATED)
async def criar_amigo(amigo: Amigo):
    """Cria um novo amigo"""
    try:
        amigo_criado = criar_amigo_db(amigo)
        logging.info(f"Amigo criado | ID: {amigo.id} | Nome: {amigo.nome}")
        return amigo_criado
    except ValueError as e:
        logging.error(f"Erro ao criar amigo: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/amigos/", response_model=List[Amigo])
async def listar_amigos():
    """Lista todos os amigos cadastrados"""
    return carregar_amigos()

@app.get("/amigos/{amigo_id}", response_model=Amigo)
async def obter_amigo(amigo_id: int):
    """Obtém um amigo específico pelo ID"""
    amigo = next((a for a in carregar_amigos() if a.id == amigo_id), None)
    if not amigo:
        logging.warning(f"Amigo não encontrado | ID: {amigo_id}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Amigo com ID {amigo_id} não encontrado")
    return amigo

@app.put("/amigos/{amigo_id}", response_model=Amigo)
async def atualizar_amigo(amigo_id: int, amigo: Amigo):
    """Atualiza um amigo existente"""
    try:
        amigo_atualizado = atualizar_amigo_db(amigo_id, amigo)
        if amigo_atualizado is None:
            logging.warning(f"Amigo não encontrado para atualização | ID: {amigo_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Amigo com ID {amigo_id} não encontrado")
        logging.info(f"Amigo atualizado | ID Antigo: {amigo_id} | Novo ID: {amigo.id}")
        return amigo_atualizado
    except ValueError as e:
        logging.error(f"Erro ao atualizar amigo: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/amigos/{amigo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_amigo(amigo_id: int):
    """Remove um amigo pelo ID"""
    if not deletar_amigo(amigo_id):
        logging.warning(f"Tentativa de excluir amigo não encontrado | ID: {amigo_id}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Amigo com ID {amigo_id} não encontrado")
    logging.info(f"Amigo excluído | ID: {amigo_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/amigos/contagem/")
async def contar_amigos():
    """Retorna a quantidade de amigos cadastrados"""
    return {"quantidade": contar_entidades("amigos")}

@app.get("/amigos/filtrar/")
async def filtrar_amigos(
    nome: Optional[str] = None,
    email: Optional[str] = None
):
    """Filtra amigos por parâmetros"""
    amigos = carregar_amigos()
    
    if nome:
        amigos = [a for a in amigos if nome.lower() in a.nome.lower()]
    if email:
        amigos = [a for a in amigos if a.email and email.lower() in a.email.lower()]
    
    logging.info(f"Filtro aplicado | Amigos encontrados: {len(amigos)}")
    return amigos

@app.get("/amigos/zip/")
async def download_zip_amigos():
    """Gera e disponibiliza download do arquivo ZIP com amigos"""
    zip_path = compactar_csv_para_zip("amigos")
    logging.info("Arquivo ZIP de amigos gerado com sucesso")
    return FileResponse(zip_path, filename="amigos.zip")

@app.get("/amigos/hash/")
async def hash_amigos():
    """Retorna hash SHA256 do arquivo de amigos"""
    hash_value = calcular_hash_csv("amigos")
    logging.info(f"Hash SHA256 calculado para amigos: {hash_value}")
    return {"hash_sha256": hash_value}

@app.get("/amigos/xml/")
async def xml_amigos():
    """Converte e disponibiliza dados dos amigos em XML"""
    xml_path = converter_csv_para_xml("amigos")
    logging.info("Arquivo XML de amigos gerado com sucesso")
    return FileResponse(xml_path, filename="amigos.xml")

# ========== Endpoints para Empréstimos ==========
@app.post("/emprestimos/", response_model=Emprestimo, status_code=status.HTTP_201_CREATED)
async def criar_emprestimo(emprestimo: Emprestimo):
    """Cria um novo empréstimo"""
    try:
        emprestimo_criado = criar_emprestimo_db(emprestimo)
        logging.info(f"Empréstimo criado | ID: {emprestimo.id}")
        return emprestimo_criado
    except ValueError as e:
        logging.error(f"Erro ao criar empréstimo: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/emprestimos/", response_model=List[Emprestimo])
async def listar_emprestimos():
    """Lista todos os empréstimos cadastrados"""
    return carregar_emprestimos()

@app.get("/emprestimos/{emprestimo_id}", response_model=Emprestimo)
async def obter_emprestimo(emprestimo_id: int):
    """Obtém um empréstimo específico pelo ID"""
    emprestimo = next((e for e in carregar_emprestimos() if e.id == emprestimo_id), None)
    if not emprestimo:
        logging.warning(f"Empréstimo não encontrado | ID: {emprestimo_id}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Empréstimo com ID {emprestimo_id} não encontrado")
    return emprestimo

@app.put("/emprestimos/{emprestimo_id}", response_model=Emprestimo)
async def atualizar_emprestimo(emprestimo_id: int, emprestimo: Emprestimo):
    """Atualiza um empréstimo existente"""
    try:
        emprestimo_atualizado = atualizar_emprestimo_db(emprestimo_id, emprestimo)
        if emprestimo_atualizado is None:
            logging.warning(f"Empréstimo não encontrado para atualização | ID: {emprestimo_id}")
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Empréstimo com ID {emprestimo_id} não encontrado")
        logging.info(f"Empréstimo atualizado | ID Antigo: {emprestimo_id} | Novo ID: {emprestimo.id}")
        return emprestimo_atualizado
    except ValueError as e:
        logging.error(f"Erro ao atualizar empréstimo: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/emprestimos/{emprestimo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_emprestimo(emprestimo_id: int):
    """Remove um empréstimo pelo ID"""
    if not deletar_emprestimo(emprestimo_id):
        logging.warning(f"Tentativa de excluir empréstimo não encontrado | ID: {emprestimo_id}")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Empréstimo com ID {emprestimo_id} não encontrado")
    logging.info(f"Empréstimo excluído | ID: {emprestimo_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/emprestimos/contagem/")
async def contar_emprestimos():
    """Retorna a quantidade de empréstimos cadastrados"""
    return {"quantidade": contar_entidades("emprestimos")}

@app.get("/emprestimos/filtrar/")
async def filtrar_emprestimos(
    jogo_id: Optional[int] = None,
    amigo_id: Optional[int] = None
):
    """Filtra empréstimos por parâmetros"""
    emprestimos = carregar_emprestimos()
    
    if jogo_id:
        emprestimos = [e for e in emprestimos if e.jogo_id == jogo_id]
    if amigo_id:
        emprestimos = [e for e in emprestimos if e.amigo_id == amigo_id]
    
    logging.info(f"Filtro aplicado | Empréstimos encontrados: {len(emprestimos)}")
    return emprestimos

@app.get("/emprestimos/zip/")
async def download_zip_emprestimos():
    """Gera e disponibiliza download do arquivo ZIP com empréstimos"""
    zip_path = compactar_csv_para_zip("emprestimos")
    logging.info("Arquivo ZIP de empréstimos gerado com sucesso")
    return FileResponse(zip_path, filename="emprestimos.zip")

@app.get("/emprestimos/hash/")
async def hash_emprestimos():
    """Retorna hash SHA256 do arquivo de empréstimos"""
    hash_value = calcular_hash_csv("emprestimos")
    logging.info(f"Hash SHA256 calculado para empréstimos: {hash_value}")
    return {"hash_sha256": hash_value}

@app.get("/emprestimos/xml/")
async def xml_emprestimos():
    """Converte e disponibiliza dados dos empréstimos em XML"""
    xml_path = converter_csv_para_xml("emprestimos")
    logging.info("Arquivo XML de empréstimos gerado com sucesso")
    return FileResponse(xml_path, filename="emprestimos.xml")