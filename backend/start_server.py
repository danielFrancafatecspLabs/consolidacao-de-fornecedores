from app.main import app

def run():
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8001)

if __name__ == '__main__':
    run()
