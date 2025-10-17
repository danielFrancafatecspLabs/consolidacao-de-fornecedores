import { getDB } from '../config/db.js';

export async function getAllFornecedores() {
  const db = getDB();
  return db.collection('fornecedores').find({}).toArray();
}

export async function getFornecedoresHoras() {
  const db = getDB();
  return db
    .collection('fornecedores')
    .aggregate([
      { $group: { _id: '$fornecedor', total_horas: { $sum: '$total_horas' } } },
      { $sort: { total_horas: -1 } },
    ])
    .toArray();
}

export async function insertSampleToDB(parsedData) {
  const db = getDB();
  await db.collection('fornecedores').deleteMany({});
  if (parsedData.length > 0) {
    await db.collection('fornecedores').insertMany(parsedData);
    return {
      message: `Inseridos ${parsedData.length} fornecedores com sucesso!`,
    };
  } else {
    throw new Error('Nenhum dado válido para inserir.');
  }
}
