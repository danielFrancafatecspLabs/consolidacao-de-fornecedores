import pandas as pd
from pymongo import MongoClient
import os

# Configurações do MongoDB
MONGO_URI = "mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net/"
DATABASE_NAME = "all_partners"
COLLECTION_NAME = "fornecedores"

# Caminho do arquivo Excel
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "DQF - 122192 - Projeto Novas Réguas Cobrança Residencial v5.xlsx")
SHEET_NAME = "ANEXO 1 - Detalhes Técnicos"

def process_and_store_excel():
    # Ler o arquivo Excel
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        
        # Transformar os dados em dicionários para inserção no MongoDB
        data = df.to_dict(orient="records")

        # Conectar ao MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Inserir os dados na coleção "fornecedores"
        collection.insert_many(data)
        print(f"Dados inseridos com sucesso na coleção '{COLLECTION_NAME}'.")
    except Exception as e:
        print(f"Erro ao processar o arquivo Excel: {e}")

if __name__ == "__main__":
    process_and_store_excel()