# Guia do Showcase de Machine Learning: JusTRT6 Search

Este documento descreve as implementações de Ciência de Dados e MLOps realizadas para validar o motor de busca semântica do JusTRT6 Search, seguindo os requisitos da CESAR School.

## 1. Estabilização do Ambiente
Para garantir a compatibilidade entre as bibliotecas de Machine Learning (`mlflow`, `scikit-learn`) e o ecossistema Python moderno, o projeto foi migrado para o **Python 3.12**. 
- **Motivo**: Conflitos de compatibilidade do `protobuf` e `mlflow` com o Python 3.14.
- **Como verificar**: O arquivo `.python-version` na raiz está pinado em `3.12.3`.

## 2. Análise Visual e Interpretabilidade (Notebook)
Foi criado um Jupyter Notebook avançado para provar que o modelo de embeddings "entende" o domínio jurídico.

- **Localização**: `notebooks/analise_e_interpretacao.ipynb`
- **Técnica Utilizada**: **UMAP** (Uniform Manifold Approximation and Projection).
- **O que ele faz**:
    1. Conecta ao banco PostgreSQL real.
    2. Recupera os embeddings de 384 dimensões gerados pelo modelo `MiniLM-L12`.
    3. Reduz a dimensionalidade para 2D.
    4. Gera um gráfico de dispersão colorido por **resultado_reclamante**.
- **Como rodar**:
    ```bash
    uv run jupyter notebook notebooks/analise_e_interpretacao.ipynb
    ```

## 3. Benchmark de Performance (MLflow)
Implementamos um script de validação rigorosa que atua como o "juiz" da qualidade da busca.

- **Localização**: `scripts/validate_search.py`
- **Golden Set**: O script utiliza um conjunto de 5 queries "gabarito" para testar se o sistema traz os processos corretos no topo.
- **Métricas Registradas**:
    - `avg_latency_ms`: Tempo médio de resposta do pgvector (~26ms).
    - `precision_at_3`: Porcentagem de acerto nos 3 primeiros resultados.

### Como abrir o painel do MLflow:
O MLflow registra cada "corrida" de teste, permitindo comparar a evolução do modelo.
1. Na raiz do projeto, execute:
   ```bash
   uv run mlflow ui
   ```
2. Abra o navegador em: `http://localhost:5000`
3. Selecione o experimento **"JusTRT6-Semantic-Search"**.
4. Lá você verá os parâmetros do modelo e os gráficos de métricas.

## 4. Integração com o Banco de Dados
A análise utiliza o **PostgreSQL** com a extensão **pgvector**.
- Tabela principal de dados: `core_analise`.
- O notebook e o script de validação extraem os vetores diretamente da coluna `embedding`.

---

## 5. Resumo Técnico para a Banca
- **Modelo de Embedding**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (SOTA para textos multilíngues curtos).
- **Lógica de Pesos**: O modelo utiliza o mecanismo de **Atenção (Self-Attention)** do Transformer para dar pesos diferentes a palavras jurídicas irrelevantes vs. termos fáticos determinantes.
- **Validação**: A solução foi validada não por um novo treinamento, mas pela **Eficácia de Recuperação** e **Coesão de Clusters**, garantindo que o espaço vetorial reflete a realidade das decisões do TRT6.
