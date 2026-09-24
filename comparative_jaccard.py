# ---------------------------------------------------------------------------------------------- #
#    BIBLIOTECAS
# ---------------------------------------------------------------------------------------------- #

import logging
import re
import string
import numpy as np
import pandas as pd

# Configuracao log

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------------------------- #
#    FUNCOES GERAIS
# ---------------------------------------------------------------------------------------------- #

def text_to_set(text: str) -> set:
    
    """
    Converte uma string de texto em um conjunto (set) de palavras únicas normalizadas.

    Passos executados:
    1. Converte todos os caracteres para letras minúsculas.
    2. Remove todas as pontuações presentes na string.
    3. Tokeniza o texto dividindo-o por espaços em branco.
    4. Retorna um set contendo apenas palavras únicas para mitigar duplicidades.

    Parâmetros:
        text (str): Texto bruto a ser processado.

    Retorno:
        set: Conjunto de palavras limpas e tokenizadas.
        
    """
    if not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = re.sub(f"[{string.punctuation}]", "", text)
    
    # Criacao dos tokens
    words = text.split()
    return set(words)


def jaccard_similarity(set1: set, set2: set) -> float:
    
    """
    Calcula o coeficiente de similaridade de Jaccard entre dois conjuntos.

    A similaridade de Jaccard é definida como o tamanho da interseção dividido pelo tamanho da união dos dois conjuntos.

    Parâmetros:
        set1 (set): Primeiro conjunto de elementos.
        set2 (set): Segundo conjunto de elementos.

    Retorno:
        float: Valor entre 0.0 e 1.0 representando o grau de similaridade.
        
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union != 0 else 0.0


def compare_tables(data: pd.DataFrame, table_col: str, db_col: str, schema_col: str, field_col: str) -> pd.DataFrame:
    
    """
    Compara o conteúdo de diferentes tabelas com base nos nomes de seus campos utilizando a métrica de similaridade de Jaccard.

    Parâmetros:
        data (pd.DataFrame): DataFrame contendo os metadados das tabelas e colunas.
        table_col (str): Nome da coluna que identifica a tabela.
        db_col (str): Nome da coluna que identifica o banco de dados.
        schema_col (str): Nome da coluna que identifica o schema.
        field_col (str): Nome da coluna que identifica o campo/coluna da tabela.

    Retorno:
        pd.DataFrame: Matriz de similaridade em formato de DataFrame pandas, onde linhas e colunas são os identificadores completos das tabelas.
    
    """
    logger.info("Iniciando o processo de agrupamento e normalização dos textos das tabelas")

    # Criação coluna chave da tabela (database.schema.tabela)
    
    data["full_table_id"] = data[db_col].astype(str) + "." + data[schema_col].astype(str) + "." + data[table_col].astype(str)
    unique_tables = data["full_table_id"].unique()
    
    table_texts = {}

    # Iterar por cada tabela única para consolidar o vocabulário de seus campos
    
    for table_id in unique_tables:
        
        # Filtrar apenas as linhas correspondentes à tabela atual
        table_data = data[data["full_table_id"] == table_id]
        
        # Concatenar todos os nomes de campos da tabela em uma única string espaçada
        concatenated_text = " ".join(table_data[field_col].astype(str).tolist())
        table_texts[table_id] = text_to_set(concatenated_text)

    logger.info(f"Total de tabelas únicas mapeadas: {len(unique_tables)}. Calculando matriz de similaridade.")

    # Construção matriz de similaridade
    
    table_ids = list(table_texts.keys())
    num_tables = len(table_ids)
    similarity_matrix = np.zeros((num_tables, num_tables))

    # Comparar combinações possíveis de tabelas
    
    for i in range(num_tables):
        for j in range(num_tables):
            similarity_matrix[i, j] = jaccard_similarity(
                table_texts[table_ids[i]], 
                table_texts[table_ids[j]]
            )
    
    similarity_df = pd.DataFrame(similarity_matrix, index=table_ids, columns=table_ids)
    
    logger.info("Matriz de similaridade calculada com sucesso.")
    
    return similarity_df


# ---------------------------------------------------------------------------------------------- #
#    FLUXO PRINCIPAL DE EXECUÇÃO
# ---------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    
    # Coluna csv entrada
    
    TABLE_COL = "TABELA"
    DB_COL = "DATABASE"
    SCHEMA_COL = "SCHEMA"
    FIELD_COL = "CAMPO"

    # Paths origem / destino
    CSV_PATH = "tables.csv"
    OUTPUT_CSV_PATH = "jaccard_similarity.csv"

    try:
        logger.info(f"Lendo o arquivo de dados em: {CSV_PATH}")
        data = pd.read_csv(CSV_PATH)
        
        similarity_df = compare_tables(data, TABLE_COL, DB_COL, SCHEMA_COL, FIELD_COL)
        similarity_df.to_csv(OUTPUT_CSV_PATH)
        logger.info(f"Matriz de similaridade entre tabelas salva com sucesso em: {OUTPUT_CSV_PATH}")

    except FileNotFoundError:
        logger.error(f"O arquivo de entrada '{CSV_PATH}' não foi encontrado. Verifique o caminho especificado.")
        
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante a execução do script: {e}")
