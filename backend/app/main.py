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

def normalize_supplier_name(name: str) -> str:
    """Normaliza o nome do fornecedor (Capitalize, evitando erros em nomes vazios)."""
    if not name:
        return ""
    # Converte para minúsculas antes de capitalizar
    return name.lower().capitalize()


# --- Endpoints da API ---

@app.post('/upload-csv', response_class=Response, status_code=201)
async def upload_xlsx(file: UploadFile = File(...)) -> Response:
    """Processa o upload de um arquivo XLSX contendo dados de fornecedores."""
    if not file.filename.lower().endswith(('xlsx',)):
        raise HTTPException(
            status_code=400, 
            detail="Apenas arquivos .xlsx são permitidos."
        )

    tmp_path = None
    logger.info(f"Upload iniciado: filename={file.filename}")
    
    try:
        # Leitura assíncrona do conteúdo do arquivo (melhor para arquivos grandes)
        contents = await file.read()
        
        # Garantindo que é bytes (embora `await file.read()` já retorne `bytes`)
        if isinstance(contents, str):
             contents = contents.encode('utf-8')
             
        file_hash = calculate_file_hash(contents)
        logger.info(f"File hash: {file_hash}")

        # --- Verificação de Duplicidade ---
        uploads_col = db.get_collection('uploads')
        existing_upload = uploads_col.find_one({'file_hash': file_hash})
        if existing_upload:
            upload_id = str(existing_upload.get('upload_id'))
            raise HTTPException(
                status_code=400, 
                detail=f"Arquivo já enviado anteriormente com ID: {upload_id}",
                # JSONResponse permite incluir dados adicionais no corpo do erro.
                headers={"X-Upload-ID": upload_id} 
            )

        # --- Escrita do Arquivo Temporário ---
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        logger.info(f"Arquivo temporário escrito em: {tmp_path}")

        # --- Parsing do Arquivo ---
        try:
            logger.info(f"Iniciando parsing do arquivo: {tmp_path}")
            suppliers = parse_fornecedores_from_xlsx(tmp_path)
            logger.info(f"Parsing concluído. Total de fornecedores extraídos: {len(suppliers)}")
        except Exception as e:
            logger.error(f"[ERRO DETALHADO] Falha ao processar o arquivo {file.filename}: {e}", exc_info=True)
            print(f"[ERRO DETALHADO] Falha ao processar o arquivo {file.filename}: {e}")
            # Registrar erro de processamento
            uploads_col.insert_one({
                'upload_id': str(uuid.uuid4()),
                'filename': file.filename,
                'file_hash': file_hash,
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'rows': 0
            })
            raise HTTPException(
                status_code=400, 
                detail=f"Erro ao processar o arquivo: {str(e)}"
            )

        logger.info(f"Fornecedores processados: {len(suppliers)}")
        
        # --- Validação de Dados ---
        total_rows = sum(len(s.get('detalhes', [])) for s in suppliers)
        if total_rows == 0:
            raise HTTPException(
                status_code=400, 
                detail='Arquivo não contém dados válidos de fornecedores.'
            )

        # --- Persistência no Banco de Dados ---
        upload_doc = {
            'upload_id': str(uuid.uuid4()),
            'filename': file.filename,
            'file_hash': file_hash,
            'timestamp': datetime.utcnow(),
            'rows': total_rows
        }

        uploads_col.insert_one(upload_doc)
        logger.info(f"Metadados do upload inseridos. ID: {upload_doc['upload_id']}")

        collection = db.get_collection('fornecedores')
        inserted_suppliers_info: List[Dict[str, Any]] = []
        
        # Preparar e inserir documentos de fornecedores
        documents_to_insert = []
        for s in suppliers:
            documents_to_insert.append({
                'fornecedor': s.get('fornecedor'),
                'total': s.get('total'),
                'detalhes': s.get('detalhes'),
                'upload_id': upload_doc['upload_id']
            })
        
        # Usar insert_many para melhor desempenho (bulk insert)
        if documents_to_insert:
            insert_result = collection.insert_many(documents_to_insert)
            
            # Coletar IDs inseridos e informações para a resposta
            for doc, obj_id in zip(documents_to_insert, insert_result.inserted_ids):
                # Apenas valores serializáveis são mantidos
                inserted_suppliers_info.append({
                    '_id': str(obj_id), 
                    'fornecedor': doc['fornecedor'], 
                    'total': doc['total']
                })
                
            logger.info(f"Documentos de fornecedores inseridos: {len(inserted_suppliers_info)}")
        else:
            logger.warning("Nenhum fornecedor válido para inserção.")

        # --- Construção da Resposta ---
        payload = {
            'upload': make_serializable(upload_doc), # Garante que o timestamp é string
            'inserted_count': len(inserted_suppliers_info), 
            'inserted': inserted_suppliers_info
        }
        
        # Retorna o JSON serializado corretamente
        json_bytes = safe_json_dumps(payload)
        
        # Usa StreamingResponse para evitar o jsonable_encoder do FastAPI e garantir CORS
        return StreamingResponse(
            iter([json_bytes]), 
            media_type='application/json', 
            status_code=201 # Resposta 201 Created para sucesso no upload
        )

    except HTTPException:
        # Re-raise HTTPException para ser tratado pelo FastAPI (já inclui CORS)
        raise
    except Exception as e:
        logger.error(f"Erro inesperado no upload: {e}", exc_info=True)
        # Erro interno
        raise HTTPException(
            status_code=500, 
            detail=f"Erro interno no servidor: {str(e)}"
        )
    finally:
        # --- Limpeza do Arquivo Temporário ---
        if tmp_path:
            try:
                os.remove(tmp_path)
                logger.debug(f"Arquivo temporário removido: {tmp_path}")
            except OSError as e:
                logger.warning(f"Não foi possível remover o arquivo temporário {tmp_path}: {e}")


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
        # O FastAPI é assíncrono, então as operações de I/O (MongoDB) devem ser
        # executadas em um thread pool (`run_in_threadpool`) ou com drivers async (AIO/Motor).
        # Assumindo que o `db` é síncrono, deixei como está, mas saiba que **bloqueia** o loop.
        
        # Consulta principal
        cursor = collection.aggregate(pipeline)
        results = []
        for doc in cursor:
            fornecedor_nome_lower = doc['_id']['fornecedor']
            
            # Normalização para a resposta (primeira letra maiúscula)
            fornecedor_nome = normalize_supplier_name(fornecedor_nome_lower)
            
            # Achata a lista de detalhes
            # doc['detalhes_list'] é uma lista de listas de detalhes (uma lista por documento original)
            detalhes = [
                item 
                for sublist in doc.get('detalhes_list', []) 
                for item in (sublist if isinstance(sublist, list) else [sublist])
            ]

            results.append({
                "fornecedor": fornecedor_nome,
                "total": doc.get("total", 0),
                "detalhes": detalhes # Incluindo detalhes se necessário, mas pode ser pesado
            })
        
        # Consulta de contagem total
        count_cursor = list(collection.aggregate(count_pipeline))
        total_count = count_cursor[0]['total_count'] if count_cursor else 0
        
        logger.info(f"Consulta /fornecedores. Registros retornados: {len(results)}. Total de grupos: {total_count}")
        
        # Usar JSONResponse com o make_serializable para garantir tipos BSON
        return JSONResponse({
            "data": make_serializable(results),
            "skip": skip,
            "limit": limit,
            "count": total_count, # Contagem total de grupos, não apenas da página
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


@app.get('/summary', response_model=List[Dict[str, Any]])
async def summary():
    """Retorna um resumo de fornecedores, agrupando perfis, total de valor e total de horas."""
    col = db.get_collection('fornecedores')
    
    pipeline = [
        { '$unwind': '$detalhes' },
        { 
            '$group': { 
                '_id': {
                    'fornecedor': {'$toLower': '$fornecedor'}, # Normaliza no grupo
                    'perfil': '$detalhes.perfil'
                }, 
                'total_valor': {'$sum': {'$ifNull': ['$detalhes.valor_total', 0]}}, 
                'total_hh': {'$sum': {'$ifNull': ['$detalhes.hora', 0]}} 
            } 
        },
        { 
            '$group': { 
                '_id': '$_id.fornecedor', 
                'perfis': { 
                    '$push': { 
                        'perfil': '$_id.perfil', 
                        'total_valor': '$total_valor', 
                        'total_hh': '$total_hh' 
                    } 
                }, 
                'fornecedor_total': { '$sum': '$total_valor' } 
            } 
        },
        { '$sort': { 'fornecedor_total': -1 } }
    ]
    
    try:
        cursor = col.aggregate(pipeline)
        out = []
        for d in cursor:
            # Normalizar o nome do fornecedor no resultado final
            fornecedor_nome = normalize_supplier_name(d['_id'])
            
            # Adicionar o nome do fornecedor normalizado e remover o _id
            d['fornecedor'] = fornecedor_nome 
            del d['_id']
            
            # Tratamento de NaN/Infinitos em floats (seu código original)
            for key, value in d.items():
                if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    d[key] = None # Usar None para representar NaN/Infinito

            # Tratar NaN/Infinitos dentro da lista 'perfis'
            for perfil in d.get('perfis', []):
                for key in ['total_valor', 'total_hh']:
                    value = perfil.get(key)
                    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                        perfil[key] = None

            out.append(d)
        
        # Usar JSONResponse com make_serializable
        return JSONResponse(make_serializable(out))
        
    except Exception as e:
        logger.error(f"Erro em /summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resumo: {str(e)}")


@app.get('/ping', response_class=Response)
async def ping():
    """Endpoint simples de saúde."""
    # O CORSMiddleware adiciona o cabeçalho automaticamente
    return Response('pong', media_type='text/plain')


@app.get('/whoami', response_model=Dict[str, str])
async def whoami():
    """Retorna informações do processo para depuração."""
    import sys
    info = {
        'pid': str(os.getpid()),
        'python_executable': sys.executable,
        'cwd': os.getcwd(),
    }
    # JSONResponse garante Content-Type e serialização segura
    return JSONResponse(info)