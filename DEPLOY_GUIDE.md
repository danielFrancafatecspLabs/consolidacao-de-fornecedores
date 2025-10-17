# Guia de Deploy e Execução do Projeto

## 1. Requisitos

- Node.js (recomendado v18 ou superior)
- Python 3.10+
- MongoDB Atlas (ou instância local)
- Vercel (para deploy do frontend)

## Variáveis de Ambiente

### Backend (FastAPI)

- `MONGODB_URI`: string de conexão do MongoDB Atlas (ex: `mongodb+srv://usuario:senha@cluster.mongodb.net/db?retryWrites=true&w=majority`)
- (Opcional) `PORT`: porta do servidor (Render usa automaticamente a porta do ambiente)

### Frontend (Vercel)

- `VITE_API_URL`: URL pública do backend (ex: `https://seu-backend.onrender.com`)

No Render, adicione as variáveis em **Environment > Add Environment Variable**.
No Vercel, adicione em **Project Settings > Environment Variables**.

### Instalação

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Instale dependências extras se aparecer erro de import:
pip install python-multipart pandas openpyxl xlrd
```

Se aparecer erro de conexão com o MongoDB Atlas, confira:

- A string de conexão em `backend/app/db.py` ou variável `MONGODB_URI`
- Se sua rede/firewall/VPN permite acesso ao cluster Atlas
- Teste a conexão usando o MongoDB Compass ou outro cliente

Se aparecer erro de import, instale o pacote indicado com `pip install nome-do-pacote`.

### Configuração

- Configure a string de conexão do MongoDB Atlas em `backend/app/db.py` ou via variável de ambiente `MONGODB_URI`.

### Execução

```powershell
python start_server.py
```

- O backend estará disponível em `http://127.0.0.1:8001`

## 3. Frontend (Dashboard)

### Instalação

```powershell
cd frontend
npm install
```

### Execução local

```powershell
npm run dev
```

- O frontend estará disponível em `http://localhost:5173`
- Por padrão, ele consome a API do backend em `http://127.0.0.1:8001`

### Deploy no Vercel

1. Crie uma conta em [Vercel](https://vercel.com/)
2. Importe o projeto do GitHub ou faça upload dos arquivos da pasta `frontend`
3. Configure a variável de ambiente `VITE_API_URL` (se necessário) para apontar para o backend hospedado
4. Clique em "Deploy"

## 4. Banco de Dados

- Para popular o banco, utilize os scripts em `backend/scripts/`:
  - `clear_fornecedores.py` para limpar fornecedores
  - `process_xlsx_to_json.py` para converter Excel em JSON
  - `insert_jsons_to_db.py` para inserir dados no MongoDB

## 5. Observações

- O backend pode ser hospedado em Railway, Render, Heroku, Azure ou outro serviço compatível com Python/FastAPI.
- O frontend é otimizado para Vercel, mas pode ser hospedado em outros serviços estáticos.
- Certifique-se de que o backend esteja acessível publicamente para o frontend em produção.

---

Dúvidas? Consulte os arquivos `README.md` nas pastas `backend` e `frontend` para mais detalhes.
