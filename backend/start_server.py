import os
import sys

# Ensure backend root is on path so `import app` works
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app

def run():
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)

if __name__ == '__main__':
    run()
