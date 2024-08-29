import pandas as pd
import numpy as np
import Levenshtein as lev

# Ler o CSV com tabelas
csv_path = 'tables.csv'
data = pd.read_csv(csv_path)

# Função para calcular a similaridade de Levenshtein
def levenshtein_similarity(s1, s2):
    """Calcula a similaridade de Levenshtein entre duas strings."""
    distance = lev.distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0  # Se ambos forem vazios, consideramos a similaridade como 100%
    return 1 - (distance / max_len)

# Função para comparar tabelas com base em Levenshtein
def compare_tables_levenshtein(data, table_col, db_col, schema_col, field_col):
    """Compara tabelas com base nas informações dos campos usando Levenshtein."""
    # Criar uma coluna combinada para identificação completa
    data['full_table_id'] = data[db_col] + '.' + data[schema_col] + '.' + data[table_col]
    
    # Obter todos os nomes de tabelas únicas
    unique_tables = data['full_table_id'].unique()
    table_texts = {}

    for table_id in unique_tables:
        # Filtrar dados da tabela específica
        table_data = data[data['full_table_id'] == table_id]
        
        # Concatenar o texto de todos os campos
        concatenated_text = ' '.join(table_data[field_col].astype(str).tolist())
        table_texts[table_id] = concatenated_text
    
    # Criar a matriz de similaridade
    tables = list(table_texts.keys())
    similarity_matrix = np.zeros((len(tables), len(tables)))

    for i in range(len(tables)):
        for j in range(len(tables)):
            similarity_matrix[i, j] = levenshtein_similarity(table_texts[tables[i]], table_texts[tables[j]])

    # Criar um DataFrame para visualizar a similaridade
    similarity_df = pd.DataFrame(similarity_matrix, index=tables, columns=tables)
    
    return similarity_df

# Definir colunas esperadas no CSV
table_col = 'TABELA'
db_col = 'DATABASE'
schema_col = 'SCHEMA'
field_col = 'CAMPO'

# Caminho para o arquivo CSV de saída
output_csv_path = 'levenshtein_similarity.csv'

# Comparar tabelas e calcular similaridade
similarity_df = compare_tables_levenshtein(data, table_col, db_col, schema_col, field_col)

# Salvar a matriz de similaridade em um novo arquivo CSV
similarity_df.to_csv(output_csv_path)

print(f"Matriz de Similaridade entre tabelas salva em: {output_csv_path}")
