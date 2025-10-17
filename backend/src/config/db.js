import { MongoClient } from 'mongodb';

// Conexão direta com Atlas (NÃO recomendado para produção)
const uri =
  'mongodb+srv://danielfrancaleite:consolidacaofornecedor@cluster0.ek2c8kp.mongodb.net';
const dbName = 'fornecedores_db';
let db;

export async function connectDB() {
  const client = new MongoClient(uri);
  await client.connect();
  db = client.db(dbName);
  console.log('MongoDB conectado!');
}

export function getDB() {
  if (!db) throw new Error('Banco de dados não conectado!');
  return db;
}
