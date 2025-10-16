import pandas as pd
from typing import List, Dict
import unicodedata
import string
import difflib

def normalize_string(value: str) -> str:
    """
    Normalize a string by removing accents, punctuation, and extra spaces.
    """
    if not value:
        return ""
    # Remove accents
    value = unicodedata.normalize('NFKD', value).encode('ASCII', 'ignore').decode('utf-8')
    # Remove punctuation
    value = value.translate(str.maketrans('', '', string.punctuation))
    # Convert to lowercase and strip extra spaces
    return value.strip().lower()

def _find_col_index(headers, names):
    for i, h in enumerate(headers):
        if h is None:
            continue
        hv = str(h).strip().lower()
        for name in names:
            if name.lower() == hv:
                return i
    return None


def parse_fornecedores_from_xlsx(path: str) -> List[Dict]:
    print(f"[LOG] Iniciando parse_fornecedores_from_xlsx para arquivo: {path}")
    # Sempre buscar a aba 'ANEXO 1 - Detalhes Técnicos'
    xls = pd.ExcelFile(path)
    sheet_name = None
    for name in xls.sheet_names:
        if 'anexo 1' in name.lower() and 'detalhes' in name.lower():
            sheet_name = name
            break
    if not sheet_name:
        print(f"[LOG] Aba 'ANEXO 1 - Detalhes Técnicos' não encontrada em {path}. Abas disponíveis: {xls.sheet_names}")
        return []
    df = pd.read_excel(xls, sheet_name=sheet_name)
    print(f"[LOG] DataFrame lido da aba '{sheet_name}'. Shape: {df.shape}")
    df = df.dropna(how='all')
    print(f"[LOG] DataFrame após dropna. Shape: {df.shape}")
    def norm(s):
        if s is None:
            return ""
        s = str(s)
        s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
        return s.strip().lower()
    def fuzzy_col(df, options):
        cols_norm = [norm(c) for c in df.columns]
        for opt in options:
            opt_norm = norm(opt)
            for idx, c in enumerate(cols_norm):
                if opt_norm in c:
                    return df.columns[idx]
            matches = difflib.get_close_matches(opt_norm, cols_norm, n=1, cutoff=0.5)
            if matches:
                return df.columns[cols_norm.index(matches[0])]
        return None
    print(f"[LOG] Colunas detectadas: {list(df.columns)}")
    col_fornecedor = fuzzy_col(df, ['fornecedor'])
    col_perfil = fuzzy_col(df, ['perfil', 'descricao'])
    col_valor = fuzzy_col(df, ['valor', 'total'])
    col_hh = fuzzy_col(df, ['hh'])
    col_hora = fuzzy_col(df, ['hora', 'horas'])
    col_qtde = fuzzy_col(df, ['qde', 'quantidade'])
    col_aloc = fuzzy_col(df, ['aloc', 'alocacao'])
    print(f"[LOG] Colunas mapeadas: fornecedor={col_fornecedor}, perfil={col_perfil}, valor={col_valor}, hh={col_hh}, hora={col_hora}, qtde={col_qtde}, aloc={col_aloc}")
    data = {}
    print(f"[LOG] Iniciando processamento das linhas...")
    for idx, row in enumerate(df.iterrows()):
        i, row_data = row
        print(f"[LOG] Processando linha {i}: {row_data.to_dict()}")
        fornecedor = row_data.get(col_fornecedor) if col_fornecedor else None
        perfil = row_data.get(col_perfil) if col_perfil else None
        valor = row_data.get(col_valor) if col_valor else None
        hh = row_data.get(col_hh) if col_hh else None
        hora = row_data.get(col_hora) if col_hora else None
        qtde = row_data.get(col_qtde) if col_qtde else None
        aloc = row_data.get(col_aloc) if col_aloc else None
        filled = [fornecedor, perfil, valor, hh, hora]
        if sum(1 for f in filled if f not in [None, "", 0, "-"]) < 2:
            print(f"[LOG] Linha {i} ignorada: menos de 2 campos essenciais preenchidos.")
            continue
        nome = norm(fornecedor) if fornecedor else norm(perfil)
        if not nome:
            print(f"[LOG] Linha {i} ignorada: nome vazio.")
            continue
        import math
        def to_float(v):
            if v is None or v == '' or (isinstance(v, float) and math.isnan(v)):
                return 0.0
            try:
                if isinstance(v, str):
                    v2 = v.replace('.', '').replace(',', '.')
                    return float(v2)
                return float(v)
            except Exception:
                print(f"[LOG] Erro ao converter valor para float: {v}")
                return 0.0

        def to_int(v):
            f = to_float(v)
            if f is None or (isinstance(f, float) and math.isnan(f)):
                return 0
            try:
                return int(f)
            except Exception:
                return 0

        valor_f = to_float(valor)
        hora_f = to_float(hora) if hora is not None else 0.0
        hh_f = to_float(hh) if hh is not None else 0.0
        qtde_i = to_int(qtde) if qtde is not None else 0
        aloc_i = to_int(aloc) if aloc is not None else 0
        detalhe = {
            'perfil': perfil,
            'hora': hora_f,
            'hh': hh_f,
            'qtde_recursos': qtde_i,
            'alocacao_meses': aloc_i,
            'valor_total': valor_f,
        }
        if nome not in data:
            data[nome] = {
                'fornecedor': fornecedor if fornecedor else perfil,
                'total': 0.0,
                'total_horas': 0.0,
                'detalhes': []
            }
        data[nome]['total'] += valor_f
        data[nome]['total_horas'] += hora_f if hora_f is not None else 0.0
        data[nome]['detalhes'].append(detalhe)
    print(f"[LOG] Fim do processamento. Total de fornecedores: {len(data)}")
    return list(data.values())

    # tolerant mapping for required columns (including new ones)
    idx_fornecedor = _find_col_index(headers, fornecedor_variants)
    idx_perfil = _find_col_index(headers, ['Perfil', 'perfil'])
    idx_hora = _find_col_index(headers, ['Hora', 'Horas', 'Horas Trabalhadas', 'horas'])
    idx_hh = _find_col_index(headers, ['H/H', 'H H', 'HH', 'h/h'])
    idx_valor = _find_col_index(headers, ['Total', 'Valor total', 'Valor Total', 'Valor', 'Total (R$)'])

    missing = []
    if idx_fornecedor is None:
        missing.append('Fornecedor')
    if idx_perfil is None:
        missing.append('Perfil')
    if idx_hora is None:
        missing.append('Horas')
    if idx_hh is None:
        missing.append('HH')
    if idx_valor is None:
        missing.append('Total')
    if missing:
        raise ValueError(f'Colunas obrigatórias não encontradas: {", ".join(missing)}')

    print("Headers:", headers)
    print("First few rows:", rows[header_row:header_row+5])

    data = {}
    # Processa apenas as linhas abaixo do cabeçalho
    for row in rows[header_row+1:]:
        if all(cell is None for cell in row):
            continue
        fornecedor = row[idx_fornecedor] if idx_fornecedor is not None else None
        perfil = row[idx_perfil] if idx_perfil is not None else None
        valor = row[idx_valor] if idx_valor is not None else None
        hh = row[idx_hh] if idx_hh is not None else None
        hora = row[idx_hora] if idx_hora is not None else None
        # Só processa se pelo menos dois campos essenciais estiverem preenchidos
        filled = [fornecedor, perfil, valor, hh, hora]
        if sum(1 for f in filled if f not in [None, "", 0]) < 2:
            continue
        nome = normalize_string(fornecedor)
        if not nome:
            continue  # ignora linhas sem fornecedor
        qtde = None
        aloc = None
        def to_float(v):
            if v is None or v == '':
                return 0.0
            try:
                if isinstance(v, str):
                    v2 = v.replace('.', '').replace(',', '.')
                    return float(v2)
                return float(v)
            except Exception:
                return 0.0
        valor_f = to_float(valor)
        hora_f = to_float(hora) if hora is not None else None
        hh_f = to_float(hh) if hh is not None else None
        qtde_i = int(to_float(qtde)) if qtde is not None and to_float(qtde) != 0 else None
        aloc_i = int(to_float(aloc)) if aloc is not None and to_float(aloc) != 0 else None
        detalhe = {
            'perfil': perfil,
            'hora': hora_f,
            'hh': hh_f,
            'qtde_recursos': qtde_i,
            'alocacao_meses': aloc_i,
            'valor_total': valor_f,
        }
        if nome not in data:
            data[nome] = {
                'fornecedor': fornecedor,
                'total': 0.0,
                'total_horas': 0.0,
                'detalhes': []
            }
        data[nome]['total'] += valor_f
        data[nome]['total_horas'] += hora_f if hora_f is not None else 0.0
        data[nome]['detalhes'].append(detalhe)
    return list(data.values())

def normalize_string(value: str) -> str:
    """
    Normalize a string by removing accents, punctuation, and extra spaces.
    """
    if not value:
        return ""
    # Remove accents
    value = unicodedata.normalize('NFKD', value).encode('ASCII', 'ignore').decode('utf-8')
    # Remove punctuation
    value = value.translate(str.maketrans('', '', string.punctuation))
    # Convert to lowercase and strip extra spaces
    return value.strip().lower()

def validate_and_structure_data(data: List[Dict]) -> List[Dict]:
    """
    Valida, estrutura e normaliza os dados antes de inseri-los no banco de dados.
    """
    structured_data = []

    for item in data:
        # Validação de campos obrigatórios
        fornecedor = normalize_string(item.get('fornecedor'))
        if not fornecedor or not item.get('detalhes'):
            continue

        # Validação e estruturação dos detalhes
        detalhes_validos = []
        for detalhe in item['detalhes']:
            perfil = normalize_string(detalhe['perfil'])
            if perfil and detalhe['valor_total'] > 0:
                detalhe['perfil'] = perfil
                detalhes_validos.append(detalhe)

        if detalhes_validos:
            structured_data.append({
                'fornecedor': fornecedor,
                'total': sum(d['valor_total'] for d in detalhes_validos),
                'total_horas': sum(d['hora'] for d in detalhes_validos if d.get('hora') is not None),
                'detalhes': detalhes_validos
            })

    return structured_data

# Atualize a função parse_fornecedores_from_xlsx para incluir validação e estruturação
def parse_and_validate_fornecedores(path: str) -> List[Dict]:
    """
    Processa, valida e estrutura os dados de um arquivo Excel.
    """
    raw_data = parse_fornecedores_from_xlsx(path)
    return validate_and_structure_data(raw_data)
