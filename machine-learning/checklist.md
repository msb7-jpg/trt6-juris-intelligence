# Checklist de Requisitos: Projeto Machine Learning (CESAR School)

Este documento mapeia os requisitos para validar a solução atual de **Busca Semântica** (Embeddings) sem a necessidade de treinar um modelo do zero, focando na análise de dados, pesos e visualização do espaço vetorial.

## 1. Objetivos da Solução (Análise e Interpretabilidade)

| Requisito | Status | Plano de Ação (Adaptado ao Projeto) |
| :--- | :---: | :--- |
| Leitura e análise exploratória de dados (EDA) | 🟢 OK | Notebook `notebooks/analise_e_interpretacao.ipynb` criado. |
| Construção de visualizações analíticas | 🟢 OK | Dashboard Vue.js funcional + Clusters UMAP no Notebook. |
| Validação Metodológica | 🟢 OK | Avaliação de Busca automatizada via Golden Set em `scripts/validate_search.py`. |
| Interpretabilidade e "Pesos" | 🟢 OK | Visualização de Clusters UMAP e análise de similaridade de cosseno documentada. |
| MLOps e Registro | 🟢 OK | MLflow integrado e registrando métricas de latência e precisão. |
| Conteinerização | 🟢 OK | Solução robusta em Docker Compose. |

---

## 2. Roteiro de Adaptação Técnica (Showcase para Banca)

Para bater os requisitos sem treinar um modelo "do zero", o foco será demonstrar domínio técnico sobre os **Pesos e Vetores** do modelo pré-treinado:

### A. Anatomia do Modelo de Embedding
- **O que explicar**: O modelo `paraphrase-multilingual-MiniLM-L12-v2` é um Transformer.
- **Visualização**: Gerar um exemplo de como uma frase jurídica vira um vetor de 384 dimensões. Mostrar os "pesos" (valores) desse vetor para provar a densidade da informação.
- **Similaridade**: Mostrar a matemática da **Similaridade de Cosseno** (ângulo entre vetores) para explicar por que dois casos são "parecidos" para a IA.

### B. Visualização do Espaço Vetorial (A "Prova Real")
- **Gráfico de Dispersão (t-SNE)**: 
    - Pegar todos os embeddings do banco pgvector.
    - Reduzir as dimensões para 2D.
    - Colorir os pontos por "Assunto" (ex: azul = Horas Extras, vermelho = FGTS).
    - **Resultado esperado**: Ver grupos (clusters) de pontos da mesma cor juntos. Isso prova visualmente que os pesos do modelo capturaram o conhecimento jurídico.

### C. Validação de Performance (Busca Vetorial)
- **Golden Set**: Criar 10 queries de teste.
- **Cálculo de Métrica**: "Em 9 de cada 10 buscas, o processo juridicamente mais relevante apareceu no Top 3".

### D. Governança e MLOps com MLflow (Inference-Focused)
Mesmo sem treinar o modelo, o MLflow é usado para registrar o "Estado da Arte" do seu motor de busca. Isso é o que chamamos de **Model Governance**.

**Como isso se acopla ao seu projeto:**
Você criará um script de avaliação (ex: `validate_search.py`) que faz o seguinte:

1. **Registra o Modelo em Uso**:
   - `mlflow.log_param("model_name", "MiniLM-L12-v2")`
   - `mlflow.log_param("embedding_dimension", 384)`
   - `mlflow.log_param("vector_db", "pgvector")`
   - *Isso prova que você tem controle sobre qual versão da IA está rodando.*

2. **Registra Métricas de Performance (O "Stress Test")**:
   - Você roda 50 buscas automáticas e registra:
   - `mlflow.log_metric("avg_latency_ms", 45.2)` -> Tempo que o banco leva para achar os vetores.
   - `mlflow.log_metric("precision_at_3", 0.88)` -> Quão precisos são os 3 primeiros resultados.

3. **Por que isso é bom para a nota?**:
   - Você mostra para o professor: *"Professor, este é o registro do MLflow. Veja que no dia 16/06 rodamos um teste de validação e o modelo MiniLM-L12 manteve uma latência de 45ms com 88% de precisão. Se decidirmos trocar por um modelo maior no futuro, temos essa baseline para comparar"*.

---

## 3. Estrutura de Entrega (Alinhamento)

- **notebooks/analise_e_interpretacao.ipynb**: Contendo clusterização, EDA e métricas de busca.
- **mlruns/**: Pasta gerada pelo MLflow com o registro da versão do modelo de embedding.
- **Relatório SBC**: Focando na metodologia de "Semantic Search Evaluation" em vez de "Model Training".
