import os
import tempfile
import json
import uuid
import hashlib
import math
import logging
from datetime import datetime
from typing import List, Dict, Any, Union

from fastapi import FastAPI, UploadFile, File, Response, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
# Importações relativas (assumindo que 'app.parser' e 'app.db' estão corretos)
from app.parser import parse_fornecedores_from_xlsx 
from app.db import db

# Configuração básica de log
logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.INFO)

# Tentativa de importação de BSON
try:
    from bson import ObjectId, json_util as bson_json_util
except ImportError:
    ObjectId = None
    bson_json_util = None

# --- Funções de Serialização ---

def make_serializable(obj: Any) -> Any:
    """Converte recursivamente tipos não serializáveis comuns (ObjectId, datetime) para strings."""
    import math
    if obj is None:
        return None
    if ObjectId is not None and isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat().replace('+00:00', 'Z')
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None  # ou 0.0 se preferir
        return obj
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    return obj

def safe_json_dumps(data: Any) -> bytes:
    """Serializa dados usando bson.json_util se disponível, ou fallback para json padrão com make_serializable."""
    try:
        if bson_json_util:
            return bson_json_util.dumps(data).encode('utf-8')
        else:
            return json.dumps(make_serializable(data)).encode('utf-8')
    except Exception as e:
        logger.error(f"Erro ao serializar dados: {e}")
        # Falha na serialização, usar fallback
        return json.dumps(make_serializable(data)).encode('utf-8')


# --- Configuração FastAPI ---

app = FastAPI(
    title="Dashboard Fornecedores API",
    description="API para upload e consulta de dados de fornecedores a partir de arquivos XLSX.",
    version="1.0.0"
)

# Adicionando middleware CORS (o bloco app.add_middleware abaixo é o padrão e mais limpo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Não há necessidade de 'expose_headers' se você não está usando cabeçalhos não-padrão.
)

# Seu middleware para tratar erros e garantir CORS está bom, mas vamos simplificá-lo
# e confiar no tratamento de exceções padrão do FastAPI + o CorsMiddleware acima.
# Deixei o seu middleware original como comentário, pois o `CORSMiddleware` oficial
# já adiciona os cabeçalhos em todas as respostas (sucesso e erro).

# @app.middleware("http")
# async def ensure_cors_and_safe_response(request, call_next):
#     try:
#         response = await call_next(request)
#         # O CORSMiddleware já adiciona o cabeçalho, não precisa duplicar.
#         # response.headers["Access-Control-Allow-Origin"] = "*"
#         return response
#     except Exception as exc:
#         logger.exception(f"Erro não tratado na requisição: {request.url}")
#         body = json.dumps({"detail": "Internal server error", "error": str(exc)})
#         # O CORSMiddleware adiciona o cabeçalho, mas vamos garantir o 500
#         return Response(body, media_type='application/json', status_code=500)


# --- Funções Auxiliares de Lógica de Negócio ---

def calculate_file_hash(contents: bytes) -> str:
    """Calcula o hash SHA256 do conteúdo do arquivo."""
    return hashlib.sha256(contents).hexdigest()


import difflib
def normalize_supplier_name(name: str) -> str:
    """Normaliza o nome do fornecedor (Capitalize, evitando erros em nomes vazios)."""
    if not name:
        return ""
    name = name.strip().lower()
    # Mapeamento manual
    manual_map = {
        'hitss': 'Hitss', 'hitts': 'Hitss',
        'ntt data': 'Ntt Data', 'nttdata': 'Ntt Data', 'ntt..': 'Ntt Data', 'ntt': 'Ntt Data',
        'nttdata': 'Ntt Data', 'ntt.': 'Ntt Data', 'ntt-data': 'Ntt Data',
        'sysmap': 'Sysmap', 'mobileum': 'Mobileum', 'spread': 'Spread', 'amdocs': 'Amdocs',
        'atos': 'Atos', 'oracle': 'Oracle', 'tqi': 'Tqi', 'mjv': 'Mjv', 'dxc': 'Dxc',
        'engineering': 'Engineering', 'pca': 'Pca', 'arcade': 'Arcade', 'engdb': 'Engdb',
        'csg': 'Csg', 'accenture': 'Accenture',
    }
    # Normaliza para remover espaços extras e pontuação
    import string
    name_norm = name.translate(str.maketrans('', '', string.punctuation)).replace(' ', '').lower()
    for key in manual_map:
        key_norm = key.translate(str.maketrans('', '', string.punctuation)).replace(' ', '').lower()
        if name_norm == key_norm:
            return manual_map[key]
    # Agrupamento por substring
    for key, val in manual_map.items():
        if key in name:
            return val
    # Agrupamento por similaridade
    choices = list(manual_map.keys())
    match = difflib.get_close_matches(name, choices, n=1, cutoff=0.8)
    if match:
        return manual_map[match[0]]
    return name.capitalize()


# --- Endpoints da API ---


@app.get('/fornecedores', response_model=Dict[str, Any])
async def list_fornecedores(
    skip: int = Query(0, ge=0), 
    limit: int = Query(20, ge=1, le=100)
):
    """Retorna a lista de fornecedores agrupados por nome e seus totais."""
    collection = db.get_collection('fornecedores')
    
    # A paginação deve ser aplicada após o agrupamento no MongoDB, 
    # se a intenção é paginar os grupos.

    pipeline = [
        {
            # Agrupa, converte o nome para minúsculas para evitar duplicidade devido à capitalização.
            "$group": {
                "_id": {"fornecedor": {"$toLower": "$fornecedor"}},
                "total": {"$sum": "$total"},
                "detalhes_list": {"$push": "$detalhes"} # Nome mais descritivo
            }
        },
        {"$sort": {"total": -1}}, # Ordenar do maior para o menor total
        {"$skip": skip},
        {"$limit": limit}
    ]
    
    # Pipeline para contagem total dos grupos (para metadados de paginação)
    count_pipeline = [
        {"$group": {"_id": {"$toLower": "$fornecedor"}}},
        {"$count": "total_count"}
    ]

    try:
        cursor = collection.aggregate(pipeline)
        raw_results = []
        for doc in cursor:
            fornecedor_nome_lower = doc['_id']['fornecedor']
            detalhes = [
                item 
                for sublist in doc.get('detalhes_list', []) 
                for item in (sublist if isinstance(sublist, list) else [sublist])
            ]
            raw_results.append({
                "fornecedor": fornecedor_nome_lower,
                "total": doc.get("total", 0),
                "detalhes": detalhes
            })
        # Agrupamento final por nome normalizado
        import unicodedata, string
        def norm_nome(nome):
            if not nome:
                return ""
            nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
            nome = nome.translate(str.maketrans('', '', string.punctuation)).replace(' ', '').lower()
            # Mapeamento manual
            manual_map = {
                'hitss': 'Hitss', 'hitts': 'Hitss',
                'nttdata': 'Ntt Data', 'nttdata': 'Ntt Data', 'ntt..': 'Ntt Data', 'ntt': 'Ntt Data', 'nttdata': 'Ntt Data', 'ntt.': 'Ntt Data', 'ntt-data': 'Ntt Data',
            }
            # Explicit shortcut: everything containing 'atos' maps to 'Atos'
            if 'atos' in nome:
                return 'Atos'
            return manual_map.get(nome, nome.capitalize())

        from collections import defaultdict
        agrupados = defaultdict(lambda: {"fornecedor": "", "total": 0, "detalhes": []})
        for item in raw_results:
            nome = norm_nome(item["fornecedor"])
            grupo = agrupados[nome]
            grupo["fornecedor"] = nome
            grupo["total"] += item["total"]
            grupo["detalhes"].extend(item["detalhes"])
        results = list(agrupados.values())
        total_count = len(results)
        logger.info(f"Consulta /fornecedores. Registros retornados: {len(results)}. Total de grupos: {total_count}")
        return JSONResponse({
            "data": make_serializable(results),
            "skip": skip,
            "limit": limit,
            "count": total_count,
        })
        
    except Exception as e:
        logger.error(f"Erro em /fornecedores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao consultar fornecedores: {str(e)}")


@app.get('/perfis', response_model=Dict[str, Any])
async def listar_perfis():
    """Lista todos os perfis (detalhes) agrupados por fornecedor, com o total de valor."""
    collection = db.get_collection('fornecedores')
    
    pipeline = [
        {"$unwind": "$detalhes"},
        {
            "$group": {
                "_id": {
                    "fornecedor": {"$toLower": "$fornecedor"},
                    "perfil": "$detalhes.perfil"
                },
                "valor_total": {"$sum": {"$ifNull": ["$detalhes.valor_total", 0]}}
            }
        },
        {"$sort": {"_id.fornecedor": 1, "valor_total": -1}} # Ordena por fornecedor e depois por valor
    ]
    
    try:
        cursor = collection.aggregate(pipeline)
        results = []
        
        for doc in cursor:
            fornecedor_nome = normalize_supplier_name(doc['_id']['fornecedor'])
            
            results.append({
                "fornecedor": fornecedor_nome,
                "perfil": doc['_id']['perfil'],
                "valor_total": doc.get("valor_total", 0)
            })
            
        return JSONResponse({"data": make_serializable(results), "count": len(results)})
        
    except Exception as e:
        logger.error(f"Erro em /perfis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao consultar perfis: {str(e)}")





@app.get('/fornecedores/horas', response_model=Dict[str, Any])
async def fornecedores_horas():
    """Retorna a soma total de horas por fornecedor."""
    collection = db.get_collection('fornecedores')
    pipeline = [
        {"$unwind": "$detalhes"},
        {
            "$group": {
                "_id": {"fornecedor": {"$toLower": "$fornecedor"}},
                "total_horas": {"$sum": {"$ifNull": ["$detalhes.hora", 0]}}
            }
        },
        {"$sort": {"total_horas": -1}}
    ]

    try:
        cursor = collection.aggregate(pipeline)
        results = []
        for doc in cursor:
            fornecedor_nome_lower = doc['_id']['fornecedor']
            fornecedor_nome = normalize_supplier_name(fornecedor_nome_lower)
            results.append({
                "fornecedor": fornecedor_nome,
                "total_horas": doc.get("total_horas", 0)
            })

        return JSONResponse({"data": make_serializable(results), "count": len(results)})

    except Exception as e:
        logger.error(f"Erro em /fornecedores/horas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao consultar horas por fornecedor: {str(e)}")