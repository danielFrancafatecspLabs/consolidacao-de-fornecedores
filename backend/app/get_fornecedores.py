import sys
import json
import urllib.request

url = 'http://127.0.0.1:8000/fornecedores'
try:
    with urllib.request.urlopen(url, timeout=10) as r:
        body = r.read().decode('utf-8')
        data = json.loads(body)
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print('ERROR:', e)
    sys.exit(1)
