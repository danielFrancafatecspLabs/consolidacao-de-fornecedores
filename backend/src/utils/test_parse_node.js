import { parseAndValidateFornecedores } from './parseExcel.js';
import fs from 'fs';

// Create a temporary workbook file? Instead, simulate rows by calling internal logic
// We'll create a small xlsx file using xlsx lib to match expectations
import xlsx from 'xlsx';

const rows = [
  { Fornecedor: '???', Total: 100, Horas: 10 },
  { Fornecedor: null, Total: 50, Horas: 5 },
  { Fornecedor: 'Hitss', Total: 200, Horas: 20 }
];

const ws = xlsx.utils.json_to_sheet(rows);
const wb = xlsx.utils.book_new();
xlsx.utils.book_append_sheet(wb, ws, 'ANEXO 1 - Detalhes Técnicos');
const tmpPath = './tmp_test.xlsx';
xlsx.writeFile(wb, tmpPath);

const parsed = parseAndValidateFornecedores(tmpPath);
console.log(JSON.stringify(parsed, null, 2));

fs.unlinkSync(tmpPath);
