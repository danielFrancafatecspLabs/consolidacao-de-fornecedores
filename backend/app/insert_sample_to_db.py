import os
import sys
import asyncio
from pymongo import MongoClient

# Ensure current app folder is on sys.path so local imports work when running the script directly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from parser import parse_and_validate_fornecedores
from db import db


async def insert():
    # Connect to MongoDB
    client = MongoClient('mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net/')
    db = client['all_partners']
    collection = db['fornecedores']

    # Clear existing data
    collection.delete_many({})
    print("Existing data cleared from 'fornecedores' collection.")

    # Parse, validate, and normalize data
    file_path = 'C:\\Users\\F216409\\consolidacao-de-fornecedores\\backend\\DQF - 122192 - Projeto Novas Réguas Cobrança Residencial v5.xlsx'  # Update with the actual file path
    raw_data = parse_and_validate_fornecedores(file_path)

    # Insert normalized data into the database
    if raw_data:
        collection.insert_many(raw_data)
        print(f"Inserted {len(raw_data)} records into 'fornecedores' collection.")
    else:
        print("No valid data to insert.")

    client.close()


if __name__ == '__main__':
    asyncio.run(insert())
