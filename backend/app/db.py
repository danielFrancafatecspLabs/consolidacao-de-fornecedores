import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net/")
MONGODB_DB = os.getenv("MONGODB_DB", "fornecedores_db")

# If no Atlas URI is provided, try local MongoDB for developer convenience.
if not MONGODB_URI:
    # fallback to local MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI_LOCAL', 'mongodb://localhost:27017')

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]

