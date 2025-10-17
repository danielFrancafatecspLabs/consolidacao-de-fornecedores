import os
import json
from app.parser import parse_fornecedores_from_xlsx


# Diretórios de entrada
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_DIRS = [
    os.path.join(BASE_DIR, 'frontend', 'OneDrive_9_16-10-2025')
]

for input_dir in INPUT_DIRS:
    output_dir = os.path.join(input_dir, 'json_output')
    os.makedirs(output_dir, exist_ok=True)
    xlsx_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.xlsx')]
    if not xlsx_files:
        print(f'Nenhum arquivo .xlsx encontrado em {input_dir}')
        continue
    for filename in xlsx_files:
        xlsx_path = os.path.join(input_dir, filename)
        print(f'Processando: {xlsx_path}')
        try:
            fornecedores = parse_fornecedores_from_xlsx(xlsx_path)
            print(f'Conteúdo extraído do parser para {filename}:')
            print(fornecedores)
            json_path = os.path.join(output_dir, filename.replace('.xlsx', '.json'))
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(fornecedores, f, ensure_ascii=False, indent=2)
            print(f'Salvo: {os.path.abspath(json_path)}')
        except Exception as e:
            print(f'Erro ao processar {filename}: {e}')
