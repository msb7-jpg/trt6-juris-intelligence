# Relatório Técnico Final: JusTRT6 Search
## Sistema de Busca Semântica e Análise Preditiva de Precedentes Trabalhistas

### 1. Introdução
O **JusTRT6 Search** é uma plataforma avançada de inteligência jurídica focada no Tribunal Regional do Trabalho da 6ª Região (Pernambuco). O sistema permite que advogados, empresas e trabalhadores realizem buscas por similaridade em linguagem natural, extraindo insights estratégicos de milhares de processos trabalhistas. Diferente de buscadores tradicionais baseados em palavras-chave, o JusTRT6 utiliza **embeddings semânticos** para entender o contexto jurídico das demandas.

---

### 2. Arquitetura do Sistema
O projeto é estruturado em um **monorepo** utilizando **UV Workspaces**, garantindo alta performance e gerenciamento unificado de dependências.

#### Módulos Principais:
- **`apps/api` (Core)**: Backend em Django REST Framework responsável pela persistência relacional (PostgreSQL) e vetorial (pgvector).
- **`apps/ingestion`**: Serviço de coleta de metadados da API pública do CNJ (DataJud).
- **`apps/worker-scrapper`**: Automação com Playwright para extração de PDFs do portal PJe do TRT6, incluindo resolução de Captcha via OCR.
- **`apps/worker-llm`**: Motor de inteligência que processa PDFs, extrai texto e gera análises estruturadas.
- **`shared`**: Biblioteca interna com schemas Pydantic, lógica de embeddings e clientes de infraestrutura (S3/Celery).
- **`frontend`**: Interface moderna em Vue.js para busca e visualização de dashboards jurimétricos.

---

### 3. Fluxo de Dados Ponta-a-Ponta

#### Etapa 1: Ingestão de Metadados
Tudo começa com a definição de assuntos recorrentes do CNJ (ex: Horas Extras, Verbas Rescisórias). O serviço de ingestão consulta o **DataJud**, recuperando números de processos, órgãos julgadores e movimentos processuais básicos. Esses dados são enviados para a API, que realiza a **deduplicação** e persistência inicial.

#### Etapa 2: Captura da Íntegra (Scraping)
Processos que ainda não possuem o documento PDF são identificados pela API e enviados para o `worker-scrapper`.

- **Lógica de Pendência ("Tem PDF / Não tem PDF")**: A API expõe o endpoint `GET /api/processos/nao_possuem_pdf/`, que utiliza uma verificação em duas camadas:
  1. **Banco de Dados**: Filtra processos onde o campo `pdf_url` está vazio.
  2. **Storage (MinIO)**: Para cada candidato, o sistema faz uma checagem física no bucket `pje-documents`. Se o arquivo não existir fisicamente, o processo é marcado como pendente de captura.
- **Execução do Robô**:
  1. O robô acessa o portal do TRT6.
  2. Resolve o desafio de **Captcha** utilizando o modelo de visão **ddddocr**.
  3. Baixa o PDF da íntegra e o armazena no MinIO.
  4. Dispara uma tarefa para o `worker-llm`.

#### Etapa 3: Análise Cognitiva com LLM
O `worker-llm` realiza o processamento pesado de linguagem natural:
1. **Conversão**: O PDF é convertido para Markdown usando `opendataloader_pdf`.
2. **Inferência**: O texto é enviado para uma instância local do modelo **Gemma 4** (via LM Studio/LangChain).
3. **Extração**: A IA preenche um esquema estruturado (`ProcessoAnalise`) contendo:
   - Resumo fático da causa.
   - Resumo da decisão proferida.
   - Classificação do desfecho (Procedente, Improcedente, Acordo, etc).
   - Resultado prático para o reclamante (Ganhou, Perdeu, Parcial).
   - Valores da causa e custas.
   - Palavras-chave jurídicas.

#### Etapa 4: Vetorização e Busca Semântica
Com a análise pronta, a API gera um **Embedding Vetorial** de 384 dimensões utilizando o modelo `paraphrase-multilingual-MiniLM-L12-v2`. 
- Este vetor é salvo na coluna `embedding` (tipo `VectorField` do pgvector).
- Quando o usuário digita: *"Trabalhei 12h por dia sem intervalo de almoço em Recife"*, o sistema gera o vetor dessa frase e executa uma busca por **similaridade de cosseno** no banco de dados.

---

### 4. Sincronização e Manutenção (Jobs)
Para garantir a integridade dos dados e a resiliência do pipeline, o sistema conta com rotinas de sincronização que podem ser executadas via **Django Management Commands**:

- **`sincronizar_minio`**: Reconcilia o banco de dados com o storage MinIO. Permite:
  - **Importação de Órfãos**: Cria registros no DB para PDFs que já existem no MinIO mas não estão catalogados.
  - **Trigger de Análise**: Identifica processos com PDF mas sem análise estruturada e dispara automaticamente a task Celery para o `worker-llm`.
  - **Limpeza**: Remove arquivos inválidos ou sem correspondência no banco de dados.
- **`indexar_vetores`**: Garante que todos os processos analisados possuam seu embedding calculado. É essencial para o "backfill" de dados históricos ou recuperação após migrações.
- **`atualizar_movimentos`**: Sincroniza as atualizações mais recentes do DataJud para processos já existentes na base.

---

### 5. Serviço de Notificação (Search Notifier)
O **Search Notifier** é um microserviço especializado que estende o valor da busca semântica para um modelo de monitoramento ativo:

1.  **Monitoramento**: Lê as buscas salvas pelos usuários no PostgreSQL.
2.  **Execução**: Re-executa as queries periodicamente utilizando a API de busca semântica.
3.  **Diferenciação**: Compara os resultados atuais com um histórico (`last_results`) armazenado de forma comprimida (zlib) para otimizar espaço.
4.  **Notificação**: Caso novos processos similares sejam detectados, o serviço envia um **e-mail HTML premium** para o usuário, contendo cards dos novos processos, seus resumos gerados por IA e o score de similaridade.

---

### 6. Inteligência de Negócio e Jurimetria
O sistema não apenas lista processos, mas agrega os dados para fornecer **Dashboards**:
- **Probabilidade de Êxito**: Qual a % histórica de vitórias para casos similares?
- **Ticket Médio**: Qual o valor médio das condenações para este tema?
- **Tempo de Tramitação**: Quanto tempo, em média, leva para sair a sentença?
- **Argumentação Estratégica**: Quais as súmulas e artigos da CLT mais citados em decisões favoráveis?

---

### 5. Detalhes Técnicos dos Modelos
- **LLM de Extração**: Gemma 4 (execução local para privacidade de dados e custo zero).
- **Modelo de Embedding**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- **OCR**: `ddddocr` (Deep Learning para quebra de captchas).
- **Banco Vetorial**: PostgreSQL + pgvector (HNSW index para buscas rápidas).

---

### 7. Validação de Machine Learning e MLOps
O projeto JusTRT6 Search foi validado seguindo rigorosos critérios de Ciência de Dados e Engenharia de ML:

#### A. Análise do Espaço Vetorial (Interpretabilidade)
- **Clusters de Embeddings**: Desenvolvemos um notebook (`notebooks/analise_e_interpretacao.ipynb`) que utiliza **UMAP** (Uniform Manifold Approximation and Projection) para reduzir os vetores de 384 dimensões para um plano 2D.
- **Insight**: A visualização permite confirmar que o modelo `MiniLM-L12` agrupa processos com desfechos e temas semelhantes no espaço latente, validando a eficácia dos pesos pré-treinados para o contexto jurídico brasileiro.

#### B. Benchmark de Busca (Golden Set)
Implementamos uma bateria de testes automatizada para medir a precisão da recuperação:
- **Métricas Monitoradas**: 
    - **Latência Média**: ~26ms por consulta (pgvector + HNSW).
    - **Precision@3**: Capacidade do modelo de trazer o caso mais relevante entre os 3 primeiros resultados.
- **Ambiente de Teste**: Script `scripts/validate_search.py` executando consultas em lote contra a base real do TRT6.

#### C. Governança com MLflow
Utilizamos o **MLflow** como plataforma de MLOps para registrar todos os experimentos e benchmarks:
- **Tracking**: Cada execução de validação registra automaticamente a versão do modelo, dimensões do vetor e métricas de performance.
- **Reprodutibilidade**: O painel do MLflow permite comparar a performance da busca ao longo do tempo ou após atualizações na lógica de pré-processamento de texto (Texto Canônico).

---

### 8. Stack Tecnológico Consolidado
Para garantir a reprodutibilidade e escalabilidade, o JusTRT6 utiliza as tecnologias mais modernas do mercado:
- **Linguagens**: Python 3.12 (otimizado para ML) e TypeScript (Frontend).
- **Backend**: Django REST Framework + Celery + RabbitMQ.
- **Banco de Dados**: PostgreSQL 16 + pgvector (Extensão vetorial).
- **Inteligência Artificial**:
    - **LLM**: Gemma 4 (Local via LM Studio).
    - **Embeddings**: Sentence-Transformers (`multilingual-e5`).
    - **OCR**: `ddddocr` (Deep Learning).
- **Infraestrutura**: Docker Compose, MinIO (S3 Local), UV (Package Manager).
- **MLOps**: MLflow (Tracking) e UMAP (Visualização).

---

### 9. Governança e Segurança
O sistema foi projetado com foco em **Privacidade por Design**:
1. **Dados Sensíveis**: A utilização de LLMs locais (Gemma 4) garante que o conteúdo dos processos nunca saia do servidor da aplicação para APIs de terceiros.
2. **Auditabilidade**: Todos os benchmarks e versões de modelos são registrados no **MLflow**, permitindo auditoria técnica das decisões da IA.

---

### 10. Conclusão e Próximos Passos
O **JusTRT6 Search** deixa de ser um protótipo para se tornar uma plataforma de inteligência jurídica de nível industrial. A união entre busca semântica, análise preditiva e governança de ML provê uma ferramenta indispensável para a advocacia moderna no TRT6.

**Links de Referência Interna**:
- [Guia do Showcase de ML](./GUIA_ML_SHOWCASE.md)
- [Plano de Ingestão de Dados](./INGESTION_EVENT_DRIVEN_PLAN.md)
