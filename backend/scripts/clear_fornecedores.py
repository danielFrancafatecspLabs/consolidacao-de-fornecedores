from app.db import db

def clear_fornecedores():
    db.get_collection('fornecedores').delete_many({})
    print('Todos os fornecedores foram excluídos.')

if __name__ == "__main__":
    clear_fornecedores()
