import os
import sys
from pymongo import MongoClient

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from parser import parse_and_validate_fornecedores

def insert():
    client = MongoClient('mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net/')
    db = client['all_partners']
    collection = db['fornecedores']

    collection.delete_many({})
    print("Existing data cleared from 'fornecedores' collection.")

    file_path = 'C:\\Users\\F216409\\consolidacao-de-fornecedores\\backend\\DQF - 122192 - Projeto Novas Réguas Cobrança Residencial v5.xlsx'  # Update with the actual file path
    raw_data = parse_and_validate_fornecedores(file_path)

    if raw_data:
        collection.insert_many(raw_data)
        print(f"Inserted {len(raw_data)} records into 'fornecedores' collection.")
    else:
        print("No valid data to insert.")

    client.close()

if __name__ == '__main__':
    insert()
