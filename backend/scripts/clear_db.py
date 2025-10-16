from pymongo import MongoClient

MONGODB_URI = 'mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net/'
DB_NAME = 'fornecedores_db'
COLLECTION_NAME = 'fornecedores'

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

result = collection.delete_many({})
print(f'Removidos {result.deleted_count} documentos da coleção {COLLECTION_NAME}.')

client.close()
print('Banco de dados esvaziado com sucesso.')
