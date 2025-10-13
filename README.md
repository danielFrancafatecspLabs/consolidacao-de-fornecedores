# Dashboard de Fornecedores

Projeto: Dashboard React + Python (FastAPI) + MongoDB Atlas.

Visão geral

- Frontend: React (Vite)
- Backend: FastAPI
- Banco: MongoDB Atlas (motor)

Funcionalidades principais

- Upload de arquivos XLSX. Lê a aba `Detalhes Técnicos` e extrai colunas: `Fornecedor`, `Perfil`, `Hora`, `H/H`, `Valor total`.
- Em cada upload cria uma linha por fornecedor (soma `Valor total`) e salva os detalhes no MongoDB.
- Dashboard com sidebar: Upload e Listagem (expandível por fornecedor).

Conteúdo da pasta

- backend/: API Python
- frontend/: App React

Leia os READMEs dentro de `backend` e `frontend` para instruções de instalação e execução.

Como rodar localmente (PowerShell)

1. Backend

```powershell
cd backend; python -m venv .venv; . .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
# configurar .env com MONGODB_URI e MONGODB_DB
uvicorn app.main:app --reload --port 8000
```

2. Frontend

```powershell
cd frontend; npm install; npm run dev
```
