# Dockerfile para backend FastAPI
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Copia os arquivos do backend
COPY . /app

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão do FastAPI/Uvicorn
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "start_server:app", "--host", "0.0.0.0", "--port", "8000"]
