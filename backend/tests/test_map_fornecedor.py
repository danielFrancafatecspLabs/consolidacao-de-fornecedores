from app.parser import map_fornecedor

samples = [
    'Atos',
    'ATOS ajuste da RC 100854987/3 Pedido emitido 5500508154',
    'ATOS ajuste da RC 100854987/3',
    'atos ajuste',
    'Atos S/A',
    'ATOSajuste',
]
for s in samples:
    print(repr(s), '->', map_fornecedor(s))
