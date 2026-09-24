# ---------------------------------------------------------------------------------------------- #
#    BIBLIOTECAS
# ---------------------------------------------------------------------------------------------- #

import logging
import Levenshtein as lev
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

def levenshtein_similarity(s1: str, s2: str) -> float:
    
    """
    Calcula a similaridade normalizada de Levenshtein entre duas strings.

    A métrica mede o número mínimo de edições (inserções, deleções ou substituições) necessárias para 
    transformar uma string em outra, sendo normalizada pelo comprimento máximo para retornar um valor entre 0.0 e 1.0.

    Parâmetros:
        s1 (str): Primeira string de texto.
        s2 (str): Segunda string de texto.

    Retorno:
        float: Valor entre 0.0 (totalmente diferentes) e 1.0 (idênticas).
        
    """
    
    # Garantir valores como string
    
    if not isinstance(s1, str):
        s1 = str(s1)
    if not isinstance(s2, str):
        s2 = str(s2)

    distance = lev.distance(s1, s2)
    max_len = max(len(s1), len(s2))
    
    # Se ambos os textos forem vazios, considera a similaridade máxima (1.0)
    if max_len == 0:
        return 1.0  
    
    return 1.0 - (distance / max_len)


def compare_tables_levenshtein(data: pd.DataFrame, table_col: str, db_col: str, schema_col: str, field_col: str) -> pd.DataFrame:
    
    """
    Compara o conteúdo de diferentes tabelas com base nos nomes de seus campos utilizando a distância e similaridade de Levenshtein.

    Parâmetros:
        data (pd.DataFrame): DataFrame contendo os metadados brutos das tabelas.
        table_col (str): Nome da coluna que identifica a tabela.
        db_col (str): Nome da coluna que identifica o banco de dados.
        schema_col (str): Nome da coluna que identifica o schema.
        field_col (str): Nome da coluna que identifica o campo/coluna da tabela.

    Retorno:
        pd.DataFrame: Matriz de similaridade de Levenshtein em formato DataFrame pandas, onde linhas e colunas representam os IDs 
        completos das tabelas.
        
    """
    logger.info("Iniciando o mapeamento e consolidação dos campos por tabela para Levenshtein.")

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
    
    logger.info(f"Total de tabelas mapeadas: {len(unique_tables)}. Calculando matriz de similaridade de Levenshtein.")

    # Construção da matriz de similaridade
    
    tables = list(table_texts.keys())
    num_tables = len(tables)
    similarity_matrix = np.zeros((num_tables, num_tables))

    # Comparar todas as combinações possíveis de tabelas
    
    for i in range(num_tables):
        for j in range(num_tables):
            similarity_matrix[i, j] = levenshtein_similarity(
                table_texts[tables[i]], 
                table_texts[tables[j]]
            )

    # Criar um DataFrame estruturado para visualizar a similaridade
    
    similarity_df = pd.DataFrame(similarity_matrix, index=tables, columns=tables)
    
    logger.info("Matriz de similaridade de Levenshtein calculada com sucesso.")
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
    OUTPUT_CSV_PATH = "levenshtein_similarity.csv"

    try:
        logger.info(f"Lendo o arquivo de entrada: {CSV_PATH}")
        data = pd.read_csv(CSV_PATH)
        similarity_df = compare_tables_levenshtein(data, TABLE_COL, DB_COL, SCHEMA_COL, FIELD_COL)
        similarity_df.to_csv(OUTPUT_CSV_PATH)
        logger.info(f"Matriz de Similaridade de Levenshtein salva com sucesso em: {OUTPUT_CSV_PATH}")

    except FileNotFoundError:
        logger.error(f"O arquivo '{CSV_PATH}' não foi encontrado no diretório. Verifique o caminho.")
        
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante a execução do pipeline: {e}")
