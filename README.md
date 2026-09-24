# Estudo de Similaridade de Tabelas

Este projeto consiste em uma frente de estudo focada em testar, avaliar e comparar diferentes abordagens computacionais para calcular a similaridade entre tabelas de banco de dados. O objetivo é analisar os metadados (como nomes de schemas, tabelas e campos) para identificar qual modelo é o mais eficiente para ser adaptado e implementado na estrutura de ingestão de tabelas para o Data Lakehouse visando evitar redundância de tabelas com mesma estrutura ou estrutura semelhante.

---

## Modelos Avaliados e Como Funcionam

### 1. Similaridade de Jaccard
* **O que é:** Uma métrica baseada em conjuntos de palavras (*sets*).
* **Como funciona:** O texto consolidado dos campos de cada tabela é transformado em um conjunto de palavras únicas (removendo pontuações e convertendo para letras minúsculas). O algoritmo calcula a interseção dos termos dividida pela união deles, gerando um valor que indica o quanto o vocabulário das tabelas se sobrepõe.

### 2. TF-IDF com Similaridade de Cosseno
* **O que é:** Uma abordagem estatística de Processamento de Linguagem Natural (PLN) focada na frequência dos termos.
* **Como funciona:** O modelo analisa o peso das palavras em um documento em relação aos demais, dando mais relevância a termos específicos e raros (que ajudam a diferenciar as tabelas) e penalizando palavras genéricas. Em seguida, a similaridade de cosseno mede o ângulo entre os vetores de texto resultantes para determinar a proximidade semântica entre as tabelas.

### 3. Similaridade de Levenshtein
* **O que é:** Uma métrica baseada na distância de edição entre strings.
* **Como funciona:** Calcula o número mínimo de alterações — como inserções, remoções ou substituições de caracteres — que seriam necessárias para transformar o texto de uma tabela no de outra. O resultado final é normalizado pelo comprimento máximo dos textos, indicando o quão próximas ortograficamente as tabelas são.
