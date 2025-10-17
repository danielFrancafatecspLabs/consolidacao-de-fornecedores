# Backend

Requisitos

- Python 3.10+

Instalação (Windows PowerShell)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

Variáveis de ambiente (exemplo .env)

- MONGODB_URI - string de conexão para MongoDB Atlas
- MONGODB_DB - nome do banco (ex: fornecedores_db)

Rodar

```powershell
uvicorn app.main:app --reload --port 8000
```
