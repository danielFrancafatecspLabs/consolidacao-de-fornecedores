import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.parser import parse_fornecedores_from_xlsx
from app.db import db
from datetime import datetime
import uuid
import json
from fastapi import Response
from starlette.responses import StreamingResponse
from fastapi.responses import JSONResponse
try:
    from bson import ObjectId
except Exception:
    ObjectId = None
from datetime import datetime as _dt
import hashlib
import math


def make_serializable(obj):
    """Recursively convert common non-serializable types (ObjectId, datetime) to strings."""
    if obj is None:
        return None
    if ObjectId is not None and isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, _dt):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    # primitives
    return obj


app = FastAPI(title="Dashboard Fornecedores API")

# --- Aggressive safety: patch FastAPI's jsonable_encoder to fall back to make_serializable
try:
    from fastapi import encoders as _fastapi_encoders
    _orig_jsonable_encoder = getattr(_fastapi_encoders, 'jsonable_encoder')

    def _safe_jsonable_encoder(obj, *args, **kwargs):
        try:
            return _orig_jsonable_encoder(obj, *args, **kwargs)
        except Exception:
            # fallback: convert known non-serializables (ObjectId, datetime) to primitives
            return _orig_jsonable_encoder(make_serializable(obj), *args, **kwargs)

    _fastapi_encoders.jsonable_encoder = _safe_jsonable_encoder
except Exception:
    # if for any reason fastapi.encoders isn't available, ignore — endpoints still use explicit responses
    pass


# Global exception handler to ensure responses always include CORS headers
def global_exception_handler(request, exc):
    import traceback
    traceback.print_exc()
    body = json.dumps({"detail": "Internal server error"})
    return Response(body, media_type='application/json', status_code=500, headers={"Access-Control-Allow-Origin": "*"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Refactored middleware to handle synchronous responses
@app.middleware("http")
async def ensure_cors_and_safe_response(request, call_next):
    try:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as exc:
        import traceback
        traceback.print_exc()
        body = json.dumps({"detail": "Internal server error", "error": str(exc)})
        return Response(body, media_type='application/json', status_code=500, headers={"Access-Control-Allow-Origin": "*"})


# Função para calcular o hash do conteúdo do arquivo
def calculate_file_hash(contents):
    return hashlib.sha256(contents).hexdigest()


@app.post('/upload', response_class=Response)
def upload_file(file: UploadFile = File(...)) -> Response:
    if not file.filename.lower().endswith(('xlsx',)):
        return Response(json.dumps({'detail': 'Apenas arquivos .xlsx'}), media_type='application/json', status_code=400, headers={"Access-Control-Allow-Origin": "*"})

    tmp_path = None
    print(f"DEBUG: upload start filename={file.filename}")
    try:
        contents = file.read()
        # Se contents vier como str, converte para bytes
        if isinstance(contents, str):
            contents = contents.encode('utf-8')
        file_hash = calculate_file_hash(contents)
        print(f"DEBUG: file hash={file_hash}")

        # Verificar duplicidade no banco de dados
        uploads_col = db.get_collection('uploads')
        existing_upload = uploads_col.find_one({'file_hash': file_hash})
        if existing_upload:
            return Response(json.dumps({'detail': 'Arquivo já enviado anteriormente', 'upload_id': existing_upload['upload_id']}), media_type='application/json', status_code=400, headers={"Access-Control-Allow-Origin": "*"})

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        print(f"DEBUG: wrote tmp file {tmp_path}")

        try:
            suppliers = parse_fornecedores_from_xlsx(tmp_path)
        except Exception as e:
            print(f"DEBUG: parse error: {e}")
            # Registrar erro de processamento
            uploads_col.insert_one({
                'upload_id': str(uuid.uuid4()),
                'filename': file.filename,
                'file_hash': file_hash,
                'timestamp': datetime.utcnow(),
                'error': str(e),
                'rows': 0
            })
            return Response(json.dumps({'detail': str(e)}), media_type='application/json', status_code=400, headers={"Access-Control-Allow-Origin": "*"})

        print("DEBUG: parsed suppliers count:", len(suppliers))

        # Criar metadados do upload
        upload_doc = {
            'upload_id': str(uuid.uuid4()),
            'filename': file.filename,
            'file_hash': file_hash,
            'timestamp': datetime.utcnow(),
            'rows': sum(len(s.get('detalhes', [])) for s in suppliers)
        }

        if upload_doc['rows'] == 0:
            return Response(json.dumps({'detail': 'Arquivo não contém dados válidos'}), media_type='application/json', status_code=400, headers={"Access-Control-Allow-Origin": "*"})

        uploads_col.insert_one(upload_doc)
        print("DEBUG: upload_doc inserted")

        # Persistir cada fornecedor
        collection = db.get_collection('fornecedores')
        inserted = []
        for i, s in enumerate(suppliers):
            doc = {
                'fornecedor': s.get('fornecedor'),
                'total': s.get('total'),
                'detalhes': s.get('detalhes'),
                'upload_id': upload_doc['upload_id']
            }
            try:
                res = collection.insert_one(doc)
                print("DEBUG: inserted doc", i, res.inserted_id)
                # keep only serializable values
                inserted.append({'_id': str(res.inserted_id), 'fornecedor': doc['fornecedor'], 'total': doc['total']})
            except Exception as ie:
                print(f"WARN: insert failed for supplier {doc.get('fornecedor')}: {ie}")
                # continue with next supplier
                continue

        # make upload_doc serializable (timestamp -> ISO)
        upload_doc['timestamp'] = upload_doc['timestamp'].isoformat() if hasattr(upload_doc['timestamp'], 'isoformat') else str(upload_doc['timestamp'])
        payload = {'upload': upload_doc, 'inserted_count': len(inserted), 'inserted': inserted}
        print("DEBUG: returning payload", payload)
        # Use StreamingResponse to avoid FastAPI jsonable_encoder touching the response
        try:
            # prefer bson.json_util if available to correctly serialize ObjectId/datetime
            from bson import json_util as bson_json_util
            body_str = bson_json_util.dumps(payload)
        except Exception:
            body_str = json.dumps(make_serializable(payload))
        json_bytes = body_str.encode('utf-8')
        return StreamingResponse(iter([json_bytes]), media_type='application/json', headers={"Access-Control-Allow-Origin": "*"})
    except Exception as e:
        # convert unexpected errors into HTTP 500 with a clear message and CORS header
        import traceback
        traceback.print_exc()
        body = json.dumps({'detail': 'Erro interno no servidor', 'error': str(e)})
        return Response(body, media_type='application/json', status_code=500, headers={"Access-Control-Allow-Origin": "*"})
    finally:
        if tmp_path:
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# Refactored list_fornecedores endpoint to use synchronous iteration
@app.get('/fornecedores')
def list_fornecedores(skip: int = 0, limit: int = 20):
    import logging
    logger = logging.getLogger("fornecedores_logger")
    collection = db.get_collection('fornecedores')
    try:
        max_limit = 20
        limit = min(limit, max_limit)
        pipeline = [
            {
                "$group": {
                    "_id": {"fornecedor": {"$toLower": "$fornecedor"}},
                    "total": {"$sum": "$total"},
                    "detalhes": {"$push": "$detalhes"}
                }
            },
            {"$sort": {"total": 1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        logger.info(f"Iniciando consulta /fornecedores agrupados (skip={skip}, limit={limit})")
        cursor = list(collection.aggregate(pipeline))
        results = []
        for doc in cursor:
            fornecedor_nome = doc['_id']['fornecedor']
            # Formata: primeira letra maiúscula, resto minúsculo
            if fornecedor_nome:
                fornecedor_nome = fornecedor_nome[0].upper() + fornecedor_nome[1:].lower()
            detalhes = [item for sublist in doc.get('detalhes', []) for item in (sublist if isinstance(sublist, list) else [sublist])]
            results.append({
                "fornecedor": fornecedor_nome,
                "total": doc.get("total", 0),
                "detalhes": detalhes
            })
        logger.info(f"Consulta /fornecedores agrupados finalizada. Retornados {len(results)} registros.")
        return {
            "data": results,
            "skip": skip,
            "limit": limit,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error in /fornecedores: {e}")
        return {"error": str(e)}, 500


# Refactored summary endpoint to use synchronous iteration
@app.get('/summary')
def summary():
    col = db.get_collection('fornecedores')
    pipeline = [
        { '$unwind': '$detalhes' },
        { '$group': { '_id': {'fornecedor':'$fornecedor','perfil':'$detalhes.perfil'}, 'total_valor': {'$sum': '$detalhes.valor_total'}, 'total_hh': {'$sum': '$detalhes.hora'} } },
        { '$group': { '_id': '$_id.fornecedor', 'perfis': { '$push': { 'perfil': '$_id.perfil', 'total_valor': '$total_valor', 'total_hh': '$total_hh' } }, 'fornecedor_total': { '$sum': '$total_valor' } } },
        { '$sort': { 'fornecedor_total': -1 } }
    ]
    cursor = col.aggregate(pipeline)
    out = []
    for d in cursor:
        for key, value in d.items():
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                d[key] = None if math.isnan(value) else float('1e308')
        out.append(d)
    return out


@app.get('/ping', response_class=Response)
async def ping():
    # simple health endpoint that returns plain text response
    return Response('pong', media_type='text/plain', headers={"Access-Control-Allow-Origin": "*"})


@app.get('/whoami')
async def whoami():
    """Return process info to help debug which Python/uvicorn is serving requests."""
    import sys
    info = {
        'pid': os.getpid(),
        'python_executable': sys.executable,
        'cwd': os.getcwd(),
    }
    # Use JSONResponse to ensure proper Content-Type and safe encoding
    return JSONResponse(info, headers={"Access-Control-Allow-Origin": "*"})


@app.get("/best_supplier")
def get_best_supplier():
    fornecedores = list(db.fornecedores.find())
    if not fornecedores:
        return {"error": "Nenhum fornecedor encontrado."}

    # Simplified logic to find the supplier with the highest total
    best_supplier = max(
        (f for f in fornecedores if f.get("total")),
        key=lambda f: f["total"],
        default=None,
    )

    if not best_supplier:
        return {"error": "Nenhum fornecedor válido encontrado."}

    return {
        "fornecedor": best_supplier["fornecedor"],
        "total": best_supplier["total"],
    }

