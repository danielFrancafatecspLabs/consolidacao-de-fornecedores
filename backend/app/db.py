import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
import time

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net/")

## Não usar fallback local, sempre usar Atlas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MongoDB")

# Retry logic for MongoDB connection
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

# Add timeout parameters and optional CA certificate for secure connections
CA_CERT_PATH = os.getenv("CA_CERT_PATH")  # Path to CA certificate, if required

## Não manipular replicaSet manualmente, Atlas já fornece o URI correto

# Update MongoDB connection to include server selection timeout and secure TLS configuration
# Increase server selection timeout further to handle slow cluster responses
for attempt in range(1, MAX_RETRIES + 1):
    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=120000,
            socketTimeoutMS=60000,
            connectTimeoutMS=60000,
            tls=True,
            tlsCAFile=CA_CERT_PATH if CA_CERT_PATH else None
        )
        db = client[MONGODB_DB]
        logger.info("Conectado ao MongoDB Atlas (TLS/SSL ativado)")
        break
    except Exception as e:
        logger.error("Attempt %d: Failed to connect to MongoDB Atlas. Error: %s", attempt, str(e))
        if attempt < MAX_RETRIES:
            logger.info("Retrying in %d seconds...", RETRY_DELAY)
            time.sleep(RETRY_DELAY)
        else:
            logger.critical("All connection attempts to MongoDB Atlas failed. Please check the connection string, network, and server status.")
            raise

