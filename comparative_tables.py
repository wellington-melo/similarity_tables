## BIBLIOTECAS UTILIZADAS

import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

# Baixar recursos necessários do NLTK
nltk.download('punkt')

# Ler o csv com tabelas e printar ele
csv_path = 'tables.csv'
data = pd.read_csv(csv_path)

# Extrair palavras-chave usando TF-IDF e retorna a matriz TF-IDF
def extract_keywords(texts):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(texts)
    return X

# Cálculo da similaridade de cosseno entre as chaves das tabelas
def calculate_similarity(matrix):
    return cosine_similarity(matrix)

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
        table_texts[table_id] = concatenated_text
    
    # Criar a matriz TF-IDF
    matrix = extract_keywords(list(table_texts.values()))
    
    # Calcular similaridade entre tabelas
    similarity_matrix = calculate_similarity(matrix)
    
    # Criar um DataFrame para visualizar a similaridade
    similarity_df = pd.DataFrame(similarity_matrix, index=table_texts.keys(), columns=table_texts.keys())
    
    return similarity_df

# Definir colunas esperadas no CSV
table_col = 'TABELA'
db_col = 'DATABASE'
schema_col = 'SCHEMA'
field_col = 'CAMPO'

# Caminho para o arquivo CSV de saída
output_csv_path = 'similarity_matrix.csv'

# Comparar tabelas e calcular similaridade
similarity_df = compare_tables(data, table_col, db_col, schema_col, field_col)

# Salvar a matriz de similaridade em um novo arquivo CSV
similarity_df.to_csv(output_csv_path)

print(f"Matriz de Similaridade entre tabelas salva em: {output_csv_path}")