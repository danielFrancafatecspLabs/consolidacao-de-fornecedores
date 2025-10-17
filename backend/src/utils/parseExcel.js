import xlsx from 'xlsx';

export function parseAndValidateFornecedores(filePath) {
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
    const hora =
      Number(row['Horas']) ||
      Number(row['hora']) ||
      Number(row['HH']) ||
      Number(row['total_horas']) ||
      0;
    if (!data[fornecedor]) {
      data[fornecedor] = { fornecedor, total: 0, total_horas: 0, detalhes: [] };
    }
    data[fornecedor].total += valor;
    data[fornecedor].total_horas += hora;
    data[fornecedor].detalhes.push(row);
  }
  return Object.values(data);
}
