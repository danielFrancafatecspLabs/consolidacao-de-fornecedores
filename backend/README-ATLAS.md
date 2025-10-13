# Como adicionar um IP ao Access List (MongoDB Atlas)

Este arquivo descreve duas formas de permitir um IP (por exemplo `24.239.160.133/32`) no MongoDB Atlas: via Console (UI) e via API.

1. Via UI (recomendado, simples)

- Faça login em https://cloud.mongodb.com
- Selecione o projeto (Project) correto no topo esquerdo
- No menu lateral, vá para Network Access
- Clique em "Add IP Address" (ou "Add Entry")
- Em "Whitelist Entry" cole o IP `24.239.160.133/32`
- Em Description insira um nome, ex: `Dev - IP unico`
- Clique em Confirm/Save

Observações: pode levar alguns segundos para propagar.

2. Via API (automação)

Requisitos:

- Uma Public Key e Private Key da API do Atlas (Project-level API Keys). Crie em Project > Access Manager > API Keys ou Organization > Access Manager.
- Project ID (também chamado de Group ID) do projeto Atlas.
- curl disponível no sistema (use `curl.exe` no Windows para chamar o binário nativo)

Exemplo de comando curl (substitua as variáveis):

```powershell
curl.exe --digest -u "<PUBLIC_KEY>:<PRIVATE_KEY>" -X POST "https://cloud.mongodb.com/api/atlas/v1.0/groups/<PROJECT_ID>/accessList" -H "Content-Type: application/json" -d '{"ipAddress":"24.239.160.133/32","comment":"added via script"}'
```

Se preferir, existe um script PowerShell de exemplo: `backend/scripts/add_atlas_ip.ps1` que pede as keys/ID ou lê as variáveis de ambiente `ATLAS_PUBLIC_KEY`, `ATLAS_PRIVATE_KEY`, `ATLAS_PROJECT_ID`. O script executa o curl e mostra o resultado.
