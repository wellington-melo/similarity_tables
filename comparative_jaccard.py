import pandas as pd
import re
import numpy as np
import string

# Função para converter texto em conjunto de palavras
def text_to_set(text):
    # Converter texto para minúsculas e remover pontuações
    text = text.lower()
    text = re.sub(f'[{string.punctuation}]', '', text)
    # Tokenizar texto em palavras e criar um conjunto
    words = text.split()
    return set(words)

# Calcular a similaridade de Jaccard entre dois conjuntos de palavras
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

# Comparar tabelas com base nos campos e chave primária
def compare_tables(data, table_col, db_col, schema_col, field_col):
    """Compara tabelas com base nas informações dos campos."""
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
        table_texts[table_id] = text_to_set(concatenated_text)
    
    # Criar a matriz de similaridade de Jaccard
    table_ids = list(table_texts.keys())
    num_tables = len(table_ids)
    similarity_matrix = np.zeros((num_tables, num_tables))

    for i in range(num_tables):
        for j in range(num_tables):
            similarity_matrix[i, j] = jaccard_similarity(table_texts[table_ids[i]], table_texts[table_ids[j]])
    
    # Criar um DataFrame para visualizar a similaridade
    similarity_df = pd.DataFrame(similarity_matrix, index=table_ids, columns=table_ids)
    
    return similarity_df

# Definir colunas esperadas no CSV
table_col = 'TABELA'
db_col = 'DATABASE'
schema_col = 'SCHEMA'
field_col = 'CAMPO'

# Caminho para o arquivo CSV de entrada
csv_path = 'tables.csv'
data = pd.read_csv(csv_path)

# Caminho para o arquivo CSV de saída
output_csv_path = 'jaccard_similarity.csv'

# Comparar tabelas e calcular similaridade
similarity_df = compare_tables(data, table_col, db_col, schema_col, field_col)

# Salvar a matriz de similaridade em um novo arquivo CSV
similarity_df.to_csv(output_csv_path)

print(f"Matriz de Similaridade entre tabelas salva em: {output_csv_path}")