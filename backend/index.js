import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { MongoClient } from 'mongodb';
import xlsx from 'xlsx';
import path from 'path';

// Carrega variáveis de ambiente
dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Função utilitária para normalizar e estruturar os dados do Excel (simplificada)
function parseAndValidateFornecedores(filePath) {
  const workbook = xlsx.readFile(filePath);
  // Procura aba que contenha 'anexo 1' e 'detalhes' (case insensitive)
  const sheetName = workbook.SheetNames.find(
    (name) =>
      name.toLowerCase().includes('anexo 1') &&
      name.toLowerCase().includes('detalhes'),
  );
  if (!sheetName)
    throw new Error("Aba 'ANEXO 1 - Detalhes Técnicos' não encontrada");
  const sheet = workbook.Sheets[sheetName];
  const rows = xlsx.utils.sheet_to_json(sheet, { defval: '' });
  // Normalização básica: agrupa por fornecedor, soma total e total_horas
  const data = {};
  for (const row of rows) {
    const fornecedor =
      row['Fornecedor'] ||
      row['fornecedor'] ||
      row['FORNECEDOR'] ||
      'Desconhecido';
    const valor = Number(row['Total']) || Number(row['Valor total']) || 0;
    const hora = Number(row['Horas']) || Number(row['hora']) || 0;
    if (!data[fornecedor]) {
      data[fornecedor] = { fornecedor, total: 0, total_horas: 0, detalhes: [] };
    }
    data[fornecedor].total += valor;
    data[fornecedor].total_horas += hora;
    data[fornecedor].detalhes.push(row);
  }
  return Object.values(data);
}

// Endpoint para inserir amostra de dados a partir de um arquivo Excel
app.post('/insert_sample_to_db', async (req, res) => {
  try {
    // Caminho do arquivo fixo (ajuste conforme necessário)
    const filePath = path.resolve(
      __dirname,
      'DQF - 122192 - Projeto Novas Réguas Cobrança Residencial v5.xlsx',
    );
    const parsedData = parseAndValidateFornecedores(filePath);
    // Limpa coleção antes de inserir
    await db.collection('fornecedores').deleteMany({});
    if (parsedData.length > 0) {
      await db.collection('fornecedores').insertMany(parsedData);
      res.json({
        message: `Inseridos ${parsedData.length} fornecedores com sucesso!`,
      });
    } else {
      res.status(400).json({ error: 'Nenhum dado válido para inserir.' });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

const uri = process.env.MONGODB_URI;
const dbName = process.env.MONGODB_DB;
let db;

// Conexão com MongoDB
async function connectDB() {
  const client = new MongoClient(uri);
  await client.connect();
  db = client.db(dbName);
  console.log('MongoDB conectado!');
}

// Exemplo de rota
app.get('/', (req, res) => {
  res.json({ status: 'API Express rodando!' });
});

// Rota para buscar total de horas por fornecedor (agregação)
app.get('/fornecedores/horas', async (req, res) => {
  try {
    const result = await db
      .collection('fornecedores')
      .aggregate([
        {
          $group: { _id: '$fornecedor', total_horas: { $sum: '$total_horas' } },
        },
        { $sort: { total_horas: -1 } },
      ])
      .toArray();
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Inicialização
const port = process.env.PORT || 3001;
connectDB().then(() => {
  app.listen(port, () => {
    console.log(`Servidor Express ouvindo na porta ${port}`);
  });
});

export default app; // Para Vercel
