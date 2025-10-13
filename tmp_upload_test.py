import requests
fpath = r'C:\Users\F216409\consolidacao-de-fornecedores\backend\samples\sample1.xlsx'
url = 'http://127.0.0.1:8000/upload'
with open(fpath,'rb') as f:
    files = {'file': ('sample1.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    try:
        r = requests.post(url, files=files, timeout=20)
        print('status', r.status_code)
        print('text', r.text)
    except Exception as e:
        print('error', e)
