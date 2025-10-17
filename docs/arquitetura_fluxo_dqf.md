# Fluxo Visual Técnico para Processamento de DQFs

## **1. Upload de Arquivos**

- **Frontend**: Usuário faz upload de múltiplos arquivos `.xlsx`.
- **Tecnologias**: React, XLSX.js.

---

## **2. Processamento no Backend**

### **Etapa 1: Detecção de Aba**

- **Algoritmo**: Fuzzy Matching (fuzz.ratio > 80).
- **Tecnologias**: rapidfuzz ou fuzzywuzzy.

### **Etapa 2: Padronização de Cabeçalhos**

- **Algoritmo**: Mapeamento semântico e similaridade textual.
- **Tecnologias**: difflib.get_close_matches ou rapidfuzz.

### **Etapa 3: Normalização de Valores**

- **Algoritmo**: Conversão de tipos, correção de unidades, imputação de nulos.
- **Tecnologias**: pandas.to_numeric, to_datetime.

### **Etapa 4: Validação**

- **Algoritmo**: Regras de integridade, checagem de anomalias (z-score, IQR).
- **Tecnologias**: pandas, logs.

### **Etapa 5: Consolidação**

- **Algoritmo**: Mesclagem de datasets normalizados.
- **Tecnologias**: pandas.concat, MongoDB insert_many.

---

## **3. Persistência no MongoDB**

- **Banco de Dados**: Armazenamento consolidado e versionado.
- **Tecnologias**: MongoDB Atlas.

---

## **4. Visualização no Frontend**

### **Dashboard**

- Tabela interativa.
- Gráficos agregados (Recharts).
- Filtros dinâmicos (Zustand/Redux).

---

## **Resumo do Fluxo**

1. **Upload**: Arquivos `.xlsx` são enviados pelo frontend.
2. **Processamento**: Backend detecta aba, padroniza cabeçalhos, normaliza valores e valida dados.
3. **Persistência**: Dados são armazenados no MongoDB.
4. **Visualização**: Frontend exibe tabelas e gráficos interativos.

---

## **Próximos Passos**

1. Implementar cada etapa no backend e frontend.
2. Validar o fluxo completo com arquivos de exemplo.
3. Expandir funcionalidades do dashboard para análise avançada.
