export function normalizeFornecedorDisplay(nome) {
  const UNIDENTIFIED = 'Fornecedor não identificado';
  if (nome === null || nome === undefined) return UNIDENTIFIED;
  const s = String(nome).trim();
  if (s === '' || s === '???') return UNIDENTIFIED;
  return s;
}

export default normalizeFornecedorDisplay;
