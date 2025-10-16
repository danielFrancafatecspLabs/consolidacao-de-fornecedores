import os
import json
from pymongo import MongoClient

# Diretório dos JSONs

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_DIRS = [
    os.path.join(BASE_DIR, 'frontend', f'OneDrive_{i}_16-10-2025', 'json_output')
    for i in range(5, 9)
]

# Conexão MongoDB Atlas
MONGODB_URI = 'mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net/'
DB_NAME = 'fornecedores_db'
COLLECTION_NAME = 'fornecedores'

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


total_files = 0
for JSON_DIR in JSON_DIRS:
    if not os.path.exists(JSON_DIR):
        print(f'Pasta não encontrada: {JSON_DIR}')
        continue
    json_files = [f for f in os.listdir(JSON_DIR) if f.lower().endswith('.json')]
    print(f'Encontrados {len(json_files)} arquivos JSON em {JSON_DIR}.')
    total_files += len(json_files)
    for filename in json_files:
        json_path = os.path.join(JSON_DIR, filename)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                print(f'Formato inesperado em {filename}, ignorando.')
                continue
            valid_data = []
            for item in data:
                item['source_file'] = filename
                fornecedor = item.get('fornecedor')
                if fornecedor is not None and str(fornecedor).strip().lower() != 'nan' and str(fornecedor).strip() != '':
                    valid_data.append(item)
            if valid_data:
                collection.insert_many(valid_data)
                print(f'Inseridos {len(valid_data)} registros válidos de {filename}')
            else:
                print(f'Nenhum registro válido em {filename}')

print(f'Total de arquivos processados: {total_files}')

client.close()
print('Finalizado. Todos os JSONs foram inseridos no banco.')
