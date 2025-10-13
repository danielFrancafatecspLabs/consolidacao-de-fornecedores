import pandas as pd

# Substitua pelo caminho do arquivo contendo os dados
file_path = "dados.txt"  # Atualize para o caminho correto do arquivo

# Leia os dados do arquivo (ajuste o separador conforme necessário)
data = pd.read_csv(file_path, sep="\t", header=None)

# Renomeie as colunas (ajuste os nomes conforme necessário)
data.columns = [
    "Diretoria", "Empresa_TI", "Un_Mercado", "Sistema", "Descrição", 
    "Tipo_Detalhe_Custo", "Fornecedor", "Perfil", "Horas", "HH", 
    "Qde_Recursos", "Alocacao_Meses", "Status", "Classificacao", 
    "Total", "N_RC_QD_OR", "Tipo_Contratacao", "Proposta", 
    "Periodo_Execucao", "Condicao_Pagamento", "Tipo_Negociacao", 
    "Tecnologia_Categoria", "Centro_Custo", "CNPJ_Cod_Fornecedor", 
    "Preenchido_Financeiro", "SI", "Filial_Fabrica", "N_Conta_Contabil"
]

# Remova linhas vazias ou desnecessárias
data = data.dropna(how="all")

# Filtre apenas as linhas preenchidas
data = data[data["Descrição"].notna()]

# Salve os dados organizados em um novo arquivo
output_file = "dados_organizados.xlsx"
data.to_excel(output_file, index=False)

print(f"Dados organizados salvos em: {output_file}")