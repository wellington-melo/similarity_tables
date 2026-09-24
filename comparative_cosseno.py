# ---------------------------------------------------------------------------------------------- #
#    BIBLIOTECAS
# ---------------------------------------------------------------------------------------------- #

import logging
import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configuracao log

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Baixar recursos necessários do NLTK

nltk.download("punkt")


# ---------------------------------------------------------------------------------------------- #
#    FUNCOES GERAIS
# ---------------------------------------------------------------------------------------------- #

def extract_keywords(texts: list) -> any:
    
    """
    Extrai características textuais e gera a matriz TF-IDF (Term Frequency-Inverse Document Frequency).

    Utiliza o TfidfVectorizer do scikit-learn aplicando remoção de stop words.

    Parâmetros:
        texts (list): Lista de strings contendo os textos consolidados de cada tabela.

    Retorno:
        scipy.sparse.matrix: Matriz esparsa contendo os pesos TF-IDF dos termos.
        
    """
    logger.info("Aplicando vetorização TF-IDF nos textos das tabelas")
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(texts)
    return X


def calculate_similarity(matrix: any) -> any:
    
    """
    Calcula a similaridade de cosseno entre todos os vetores da matriz fornecida.

    Parâmetros:
        matrix (any): Matriz numérica de características (ex: matriz TF-IDF).

    Retorno:
        numpy.ndarray: Matriz quadrada de similaridade de cosseno.
        
    """
    logger.info("Calculando a similaridade de cosseno entre as matrizes de características.")
    return cosine_similarity(matrix)


def compare_tables(data: pd.DataFrame, table_col: str, db_col: str, schema_col: str, field_col: str) -> pd.DataFrame:
    
    """
    Compara o conteúdo de diferentes tabelas com base nos nomes de seus campos utilizando a vetorização TF-IDF e a Similaridade de Cosseno.

    Parâmetros:
        data (pd.DataFrame): DataFrame contendo os metadados brutos das tabelas.
        table_col (str): Nome da coluna que identifica a tabela.
        db_col (str): Nome da coluna que identifica o banco de dados.
        schema_col (str): Nome da coluna que identifica o schema.
        field_col (str): Nome da coluna que identifica o campo/coluna da tabela.

    Retorno:
        pd.DataFrame: Matriz de similaridade de cosseno em formato DataFrame pandas, onde linhas e colunas representam os IDs completos das tabelas.
    
    """
    
    logger.info("Iniciando o mapeamento e consolidação dos campos por tabela.")

    # Coluna combinada convertendo para string para garantir unicidade
    
    data["full_table_id"] = (data[db_col].astype(str) + "." + data[schema_col].astype(str) + "." + data[table_col].astype(str))
    unique_tables = data["full_table_id"].unique()
    table_texts = {}

    # Iterar por cada identificador único de tabela para concatenar seus respectivos campos
    
    for table_id in unique_tables:
        
        # Filtrar apenas as linhas pertencentes à tabela atual
        table_data = data[data["full_table_id"] == table_id]
        
        # Concatenar todos os nomes de campos em uma única string espaçada
        concatenated_text = " ".join(table_data[field_col].astype(str).tolist())
        table_texts[table_id] = concatenated_text
    
    logger.info(f"Total de tabelas mapeadas: {len(unique_tables)}. Gerando matriz TF-IDF.")

    # Matriz TF-IDF utilizando os textos consolidados
    
    matrix = extract_keywords(list(table_texts.values()))
    
    # Calcular a similaridade de cosseno com base na matriz TF-IDF gerada
    similarity_matrix = calculate_similarity(matrix)
    
    # Converter o resultado em um DataFrame estruturado utilizando as chaves das tabelas
    similarity_df = pd.DataFrame(
        similarity_matrix, 
        index=list(table_texts.keys()), 
        columns=list(table_texts.keys())
    )
    
    logger.info("Processo de comparação de tabelas concluído com sucesso.")
    return similarity_df


# ---------------------------------------------------------------------------------------------- #
#    FLUXO PRINCIPAL DE EXECUÇÃO
# ---------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    
    # Colunas csv
    TABLE_COL = "TABELA"
    DB_COL = "DATABASE"
    SCHEMA_COL = "SCHEMA"
    FIELD_COL = "CAMPO"

    # Path input / output
    CSV_PATH = "tables.csv"
    OUTPUT_CSV_PATH = "cosseno_similarity.csv"

    try:
        logger.info(f"Lendo o arquivo de entrada: {CSV_PATH}")
        data = pd.read_csv(CSV_PATH)
        similarity_df = compare_tables(data, TABLE_COL, DB_COL, SCHEMA_COL, FIELD_COL)
        similarity_df.to_csv(OUTPUT_CSV_PATH)
        logger.info(f"Matriz de Similaridade por Cosseno salva com sucesso em: {OUTPUT_CSV_PATH}")

    except FileNotFoundError:
        logger.error(f"O arquivo '{CSV_PATH}' não foi encontrado no diretório. Verifique o caminho.")
        
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante a execução do pipeline: {e}")
