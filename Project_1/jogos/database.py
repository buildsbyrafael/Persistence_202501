import csv
from typing import List, Dict, Type, TypeVar, Optional
from pathlib import Path
import logging
from pydantic import BaseModel, ValidationError
import zipfile
import hashlib
import xml.etree.ElementTree as ET
from models import Jogo, Amigo, Emprestimo

T = TypeVar('T', bound=BaseModel)

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/database.log"),
        logging.StreamHandler()
    ]
)

# Mapeamento de entidades para modelos
MODEL_POR_ENTIDADE = {
    "jogos": Jogo,
    "amigos": Amigo,
    "emprestimos": Emprestimo
}

# Funções Base
def _converter_tipos(item: Dict) -> Dict:
    """Conversão automática de tipos para valores do CSV"""
    type_conversions = {
        'id': int,
        'jogo_id': int,
        'amigo_id': int,
        'ano_lancamento': int,
        'disponivel': lambda x: str(x).lower() == 'true'
    }
    
    for field, converter in type_conversions.items():
        if field in item and item[field] not in (None, ''):
            try:
                item[field] = converter(item[field])
            except (ValueError, AttributeError) as e:
                logging.warning(f"Erro ao converter {field}: {e}")
                continue
    return item

def ler_csv(entidade: str) -> List[Dict[str, str]]:
    """Lê um arquivo CSV e retorna uma lista de dicionários"""
    arquivo = Path(f"data/{entidade}.csv")
    try:
        if not arquivo.exists():
            arquivo.parent.mkdir(exist_ok=True)
            with arquivo.open(mode="w", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=list(MODEL_POR_ENTIDADE[entidade].model_fields.keys()))
                writer.writeheader()
            return []
            
        with arquivo.open(mode="r", encoding="utf-8") as file:
            return [_converter_tipos(item) for item in csv.DictReader(file)]
    except Exception as e:
        logging.error(f"Erro ao ler {entidade}.csv: {str(e)}")
        raise

def escrever_csv(entidade: str, dados: List[Dict], model: Type[T]):
    """Escreve dados no arquivo CSV correspondente"""
    try:
        campos = list(model.model_fields.keys())
        arquivo = Path(f"data/{entidade}.csv")
        arquivo.parent.mkdir(exist_ok=True)
        
        with arquivo.open(mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=campos)
            writer.writeheader()
            writer.writerows(dados)
    except Exception as e:
        logging.error(f"Erro ao escrever {entidade}.csv: {str(e)}")
        raise

def _validar_id_existente(entidade: str, item_id: int) -> bool:
    """Verifica se um ID existe na entidade especificada"""
    dados = ler_csv(entidade)
    return any(int(item.get('id')) == item_id for item in dados)

# Operações CRUD Genéricas
def carregar_entidades(entidade: str, model: Type[T]) -> List[T]:
    """Carrega entidades do CSV e valida com o modelo Pydantic"""
    dados = ler_csv(entidade)
    entidades = []
    
    for item in dados:
        try:
            entidades.append(model.model_validate(item))
        except ValidationError as e:
            logging.error(f"Erro ao validar {entidade}: {str(e)}")
            continue
    
    logging.info(f"Carregados {len(entidades)} {entidade} do CSV")
    return entidades

def criar_entidade(entidade: str, item: BaseModel):
    """Adiciona uma nova entidade ao CSV"""
    dados = ler_csv(entidade)
    novo_item = item.model_dump()
    
    if any(int(d.get('id')) == item.id for d in dados):
        raise ValueError(f"{entidade.capitalize()} com ID {item.id} já existe")
        
    dados.append(novo_item)
    escrever_csv(entidade, dados, type(item))
    logging.info(f"{entidade.capitalize()} criado com ID {item.id}")
    return item

def atualizar_entidade(entidade: str, item_id: int, item: BaseModel) -> Optional[T]:
    """Atualiza uma entidade existente no CSV, permitindo alteração de ID"""
    dados = ler_csv(entidade)
    dados_atualizados = []
    encontrado = False
    
    # Verifica se o novo ID já existe (exceto para o próprio item)
    if item.id != item_id and any(int(ent.get('id')) == item.id for ent in dados):
        raise ValueError(f"ID {item.id} já existe na entidade {entidade}")
    
    for ent in dados:
        if int(ent.get('id')) == item_id:  # Encontrou o item a ser atualizado
            dados_atualizados.append(item.model_dump())
            encontrado = True
        else:
            dados_atualizados.append(ent)
    
    if not encontrado:
        return None
    
    escrever_csv(entidade, dados_atualizados, type(item))
    logging.info(f"{entidade.capitalize()} atualizado | ID Antigo: {item_id} | Novo ID: {item.id}")
    return item

def deletar_entidade(entidade: str, item_id: int) -> bool:
    """Remove uma entidade do CSV"""
    if not _validar_id_existente(entidade, item_id):
        return False
    
    dados = ler_csv(entidade)
    dados_filtrados = [d for d in dados if int(d.get('id')) != item_id]
    
    model = MODEL_POR_ENTIDADE.get(entidade)
    if model is None:
        raise ValueError(f"Modelo não encontrado para entidade: {entidade}")
    
    escrever_csv(entidade, dados_filtrados, model)
    logging.info(f"{entidade.capitalize()} excluído | ID: {item_id}")
    return True

# --- Operações Específicas para Jogos ---
def carregar_jogos() -> List[Jogo]:
    return carregar_entidades("jogos", Jogo)

def criar_jogo(jogo: Jogo) -> Jogo:
    return criar_entidade("jogos", jogo)

def atualizar_jogo(jogo_id: int, jogo: Jogo) -> Optional[Jogo]:
    return atualizar_entidade("jogos", jogo_id, jogo)

def deletar_jogo(jogo_id: int) -> bool:
    return deletar_entidade("jogos", jogo_id)

# --- Operações para Amigos ---
def carregar_amigos() -> List[Amigo]:
    return carregar_entidades("amigos", Amigo)

def criar_amigo(amigo: Amigo) -> Amigo:
    return criar_entidade("amigos", amigo)

def atualizar_amigo(amigo_id: int, amigo: Amigo) -> Optional[Amigo]:
    return atualizar_entidade("amigos", amigo_id, amigo)

def deletar_amigo(amigo_id: int) -> bool:
    return deletar_entidade("amigos", amigo_id)

# Operações para Empréstimos
def carregar_emprestimos() -> List[Emprestimo]:
    return carregar_entidades("emprestimos", Emprestimo)

def criar_emprestimo(emprestimo: Emprestimo) -> Emprestimo:
    # Verifica se o jogo e o amigo existem
    jogos = carregar_jogos()
    amigos = carregar_amigos()
    
    if not any(j.id == emprestimo.jogo_id for j in jogos):
        raise ValueError(f"Jogo com ID {emprestimo.jogo_id} não encontrado")
    
    if not any(a.id == emprestimo.amigo_id for a in amigos):
        raise ValueError(f"Amigo com ID {emprestimo.amigo_id} não encontrado")
    
    # Verifica se o jogo está disponível
    jogo = next(j for j in jogos if j.id == emprestimo.jogo_id)
    if not jogo.disponivel:
        raise ValueError(f"Jogo com ID {emprestimo.jogo_id} não está disponível para empréstimo")
    
    # Atualiza a disponibilidade do jogo para False
    jogo.disponivel = False
    jogos_atualizados = [j.model_dump() for j in jogos]
    escrever_csv("jogos", jogos_atualizados, Jogo)
    
    return criar_entidade("emprestimos", emprestimo)

def atualizar_emprestimo(emprestimo_id: int, emprestimo: Emprestimo) -> Optional[Emprestimo]:
    emprestimos = carregar_emprestimos()
    emprestimo_antigo = next((e for e in emprestimos if e.id == emprestimo_id), None)
    
    if not emprestimo_antigo:
        return None
    
    jogos = carregar_jogos()
    
    # Se o jogo foi alterado no empréstimo
    if emprestimo_antigo.jogo_id != emprestimo.jogo_id:
        # Libera o jogo antigo
        jogo_antigo = next((j for j in jogos if j.id == emprestimo_antigo.jogo_id), None)
        if jogo_antigo:
            jogo_antigo.disponivel = True
        
        # Reserva o novo jogo
        jogo_novo = next((j for j in jogos if j.id == emprestimo.jogo_id), None)
        if jogo_novo:
            if not jogo_novo.disponivel:
                raise ValueError(f"Jogo com ID {emprestimo.jogo_id} não está disponível")
            jogo_novo.disponivel = False
        
        # Atualiza ambos os jogos
        jogos_atualizados = [j.model_dump() for j in jogos]
        escrever_csv("jogos", jogos_atualizados, Jogo)
    
    return atualizar_entidade("emprestimos", emprestimo_id, emprestimo)

def deletar_emprestimo(emprestimo_id: int) -> bool:
    """Remove um empréstimo e atualiza a disponibilidade do jogo"""
    emprestimos = carregar_emprestimos()
    emprestimo = next((e for e in emprestimos if e.id == emprestimo_id), None)
    
    if not emprestimo:
        return False
    
    # Atualiza a disponibilidade do jogo para True
    jogos = carregar_jogos()
    jogo = next((j for j in jogos if j.id == emprestimo.jogo_id), None)
    
    if jogo:
        jogo.disponivel = True
        jogos_atualizados = [j.model_dump() for j in jogos]
        escrever_csv("jogos", jogos_atualizados, Jogo)
    
    # Agora deleta o empréstimo
    return deletar_entidade("emprestimos", emprestimo_id)

# Funções Adicionais
def contar_entidades(entidade: str) -> int:
    """Retorna a quantidade de entidades no CSV"""
    return len(ler_csv(entidade))

def compactar_csv_para_zip(entidade: str) -> Path:
    """Compacta o CSV para ZIP"""
    csv_path = Path(f"data/{entidade}.csv")
    zip_path = Path(f"data/{entidade}.zip")
    
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(csv_path, arcname=csv_path.name)
        logging.info(f"Arquivo {entidade}.zip criado com sucesso")
        return zip_path
    except Exception as e:
        logging.error(f"Erro ao compactar {entidade}.csv: {str(e)}")
        raise

def calcular_hash_csv(entidade: str) -> str:
    """Calcula hash SHA256 do CSV"""
    csv_path = Path(f"data/{entidade}.csv")
    sha256_hash = hashlib.sha256()
    
    try:
        with csv_path.open("rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Erro ao calcular hash para {entidade}.csv: {str(e)}")
        raise

def converter_csv_para_xml(entidade: str) -> Path:
    """Converte CSV para XML"""
    dados = ler_csv(entidade)
    root = ET.Element(entidade)
    
    try:
        for item in dados:
            elemento = ET.SubElement(root, entidade[:-1])  # Remove 's' final
            for chave, valor in item.items():
                ET.SubElement(elemento, chave).text = str(valor)
        
        xml_path = Path(f"data/{entidade}.xml")
        ET.ElementTree(root).write(xml_path, encoding='utf-8', xml_declaration=True)
        logging.info(f"Arquivo {entidade}.xml criado com sucesso")
        return xml_path
    except Exception as e:
        logging.error(f"Erro ao converter {entidade}.csv para XML: {str(e)}")
        raise

# Funções Auxiliares
def verificar_dados():
    """Verifica a integridade dos dados nos CSVs"""
    print("\n=== VERIFICAÇÃO DE DADOS ===")
    print(f"Jogos carregados: {len(carregar_jogos())}")
    print(f"Amigos carregados: {len(carregar_amigos())}")
    print(f"Empréstimos carregados: {len(carregar_emprestimos())}")

if __name__ == "__main__":
    # Cria a pasta data se não existir
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    verificar_dados()
