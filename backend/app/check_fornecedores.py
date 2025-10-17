import sys
import os

# ensure imports work when running script directly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from db import db
import asyncio


async def show():
    col = db.get_collection('fornecedores')
    count = await col.count_documents({})
    print('count=', count)
    cursor = col.find({}).limit(10)
    docs = []
    async for d in cursor:
        d['_id'] = str(d['_id'])
        docs.append(d)
    print('sample docs=')
    for doc in docs:
        print(doc)


if __name__ == '__main__':
    asyncio.run(show())
