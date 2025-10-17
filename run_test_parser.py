import sys
# Make sure repo root is on path
sys.path.append(r"c:\Users\F284535\Documents\ConsolidacaoFornecedores\consolidacao-de-fornecedores")
# If pandas is not installed, inject a minimal dummy so import of parser succeeds for this test
import types
if 'pandas' not in sys.modules:
    sys.modules['pandas'] = types.ModuleType('pandas')

from backend.app import parser

cases = [None, '', '   ', '???', '  ???  ', 'Hitss', 'Ntt Data']
print("map_fornecedor results:")
for c in cases:
    print(repr(c), '->', parser.map_fornecedor(c))

print("\ngroup_suppliers_by_manual_map result for sample data:")
raw = [
    {'fornecedor': None, 'total': 100.0, 'total_horas': 10.0, 'detalhes':[{'perfil':'P','hora':2,'hh':1,'qtde_recursos':1,'alocacao_meses':1,'valor_total':100.0}]},
    {'fornecedor':'???','total':50.0,'total_horas':5.0,'detalhes':[{'perfil':'P2','hora':1,'hh':1,'qtde_recursos':1,'alocacao_meses':1,'valor_total':50.0}]},
    {'fornecedor':'Hitss','total':200.0,'total_horas':20.0,'detalhes':[{'perfil':'P3','hora':3,'hh':1,'qtde_recursos':1,'alocacao_meses':1,'valor_total':200.0}]}
]

print(parser.group_suppliers_by_manual_map(raw))
