import sys
import json
import urllib.request

url = 'http://127.0.0.1:8000/fornecedores'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        body = r.read().decode('utf-8')
        data = json.loads(body)
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)

def normalize_nome(nome):
    if not nome:
        return ""
    return (
        str(nome)
        .strip()
        .lower()
        .replace("ç", "c")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("ê", "e")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ü", "u")
        .replace("î", "i")
        .replace("ï", "i")
        .replace("à", "a")
        .replace("è", "e")
        .replace("ì", "i")
        .replace("ò", "o")
        .replace("ù", "u")
        .replace("ñ", "n")
        .replace(" ", "")
    )

def get_all_fornecedores():
    from .db import db
    from .parser import FORNECEDOR_MAP, normalize_string, map_fornecedor
    fornecedores = list(db.get_collection('fornecedores').find({}, {'_id': 0}))
    agrupados = {}
    for f in fornecedores:
        # make a small, explicit shortcut: any supplier name containing 'atos'
        # (case-insensitive, normalized) should be grouped as 'Atos'.
        nome_raw = f.get('fornecedor')
        nome_norm = normalize_string(nome_raw)
        if 'atos' in nome_norm:
            nome_principal = 'Atos'
        else:
            nome_principal = map_fornecedor(nome_raw)
        if nome_principal not in agrupados:
            agrupados[nome_principal] = {
                'fornecedor': nome_principal,
                'total': 0.0,
                'total_horas': 0.0,
                'detalhes': []
            }
        agrupados[nome_principal]['total'] += float(f.get('total', 0) or 0)
        agrupados[nome_principal]['total_horas'] += float(f.get('total_horas', 0) or 0)
        if 'detalhes' in f and isinstance(f['detalhes'], list):
            agrupados[nome_principal]['detalhes'].extend(f['detalhes'])
    return list(agrupados.values())
