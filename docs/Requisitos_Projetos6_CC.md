# Projetos 6 CC — Mapeamento dos Entregáveis ao Projeto JurisTCU / TRT-6

Este documento liga cada **entregável obrigatório** da disciplina a uma **parte
concreta do projeto** (código, serviço, documento ou artefato), indicando:

- **Onde já está implementado** no repositório.
- **O que ainda falta produzir**, concentrado na frente de modelagem
  supervisionada (treino/comparação/tuning/validação), feita direto no código.

> **Contexto do produto.** O sistema coleta processos trabalhistas do **TRT-6 /
> DataJud (CNJ)**, baixa a íntegra em PDF (resolvendo captcha), extrai uma
> **análise estruturada** via LLM, gera **embeddings vetoriais** e expõe uma
> **busca semântica** em linguagem natural, além de alertas por e-mail de buscas
> salvas. O dashboard (Vue) consome esses dados.

---

## Visão geral — onde mora o "Machine Learning" no projeto

O projeto tem **três frentes de aprendizado de máquina**, em estágios diferentes
de maturidade:

| Frente | Técnica | Onde está no código | Papel |
|---|---|---|---|
| **Busca semântica vetorial** | Embeddings densos (`sentence-transformers`) + vizinhança por cosseno (pgvector) | [shared/src/shared/embeddings.py](../shared/src/shared/embeddings.py), [apps/api/core/services.py](../apps/api/core/services.py) (`buscar_processos_semanticos`) | **Recuperação / ranqueamento** por similaridade (estilo KNN) |
| **Extração estruturada da decisão** | LLM com *structured output* (Pydantic/JSON Schema) | [apps/worker-llm/main.py](../apps/worker-llm/main.py), [shared/src/shared/schemas/resumo_ia.py](../shared/src/shared/schemas/resumo_ia.py) | Gera os **rótulos** (`desfecho`, `resultado_reclamante`, …) que viram variável-alvo |
| **Reconhecimento de captcha** | OCR pré-treinado (`ddddocr`) | [apps/worker-scrapper/pje_scraper/captcha.py](../apps/worker-scrapper/pje_scraper/captcha.py) | Modelo de visão de apoio à coleta |

A **variável-alvo natural para um modelo de ML clássico treinável** (KNN,
árvore, regressão logística etc. — exigido pelos entregáveis 4 a 7) é o
**resultado da ação para o reclamante** (`resultado_reclamante`) ou o
**desfecho** (`desfecho`), definidos como enums em
[resumo_ia.py](../shared/src/shared/schemas/resumo_ia.py). Esses rótulos são
produzidos pela LLM e ficam disponíveis no banco junto a *features* estruturadas
(classe, assuntos, órgão julgador, valor da causa, palavras-chave, embedding).

---

## Mapeamento entregável a entregável

### 1. Definição formal do problema de ML

> *Tipo de problema, variável-alvo, estrutura dos dados de entrada, métrica de
> avaliação e justificativa de valor.*

**Cobertura: concluída — definição formal redigida no
[README principal](../README.md#definição-formal-do-problema-de-machine-learning).** ✅

- **Tipo de problema:**
  - *Recuperação/ranqueamento por similaridade* (não supervisionado) → busca
    semântica, já implementada.
  - *Classificação multiclasse* (supervisionado) → prever
    `resultado_reclamante` ∈ {`ganhou`, `ganhou_parcial`, `perdeu`,
    `sem_decisao`} ou `desfecho` (7 classes), a partir das *features* do
    processo. **Este é o problema a ser treinado nos entregáveis 4–7.**
- **Variável-alvo:** `resultado_reclamante` / `desfecho` —
  [resumo_ia.py:28-41](../shared/src/shared/schemas/resumo_ia.py#L28-L41).
- **Estrutura dos dados de entrada:** campos relacionais do `Processo` (classe,
  órgão julgador, assuntos, valor da causa, custas) + texto canônico montado em
  `montar_texto_indexacao` ([services.py:151-184](../apps/api/core/services.py#L151-L184))
  + vetor de 384 dimensões em `Analise.embedding`.
- **Métrica de avaliação:** para a busca, similaridade de cosseno / precisão no
  top-k; para a classificação, *accuracy*, *F1 macro* e matriz de confusão.
- **Onde está formalizado:** seção *Definição formal do problema de Machine
  Learning* no [README principal](../README.md).
- **Referência de apoio:** [docs/BuscaVetorial_MVP.md](./BuscaVetorial_MVP.md).

---

### 2. Plano técnico de dados + viabilidade

> *Fontes (abertas/próprias/simuladas), formatos, volume, desafios e viabilidade.*

**Cobertura: forte — já existe pipeline de coleta real.**

- **Fontes:**
  - *Aberta:* dataset HuggingFace `LeandroRibeiro/JurisTCU` — [README.md:3](../README.md#L3) e comando `load_juristcu`.
  - *Aberta (API pública):* **DataJud / CNJ — TRT-6**, consultada em lotes —
    [services.py:389-413](../apps/api/core/services.py#L389-L413).
  - *Própria (coleta automatizada):* scraping da íntegra no **PJe TRT-6** com
    resolução de captcha — [apps/worker-scrapper/README.md](../apps/worker-scrapper/README.md).
  - *Simulada/exemplo:* JSONs por assunto em
    [apps/ingestion/src/ingestion/data/](../apps/ingestion/src/ingestion/data/)
    e [apps/api/data/dataJud.json](../apps/api/data/dataJud.json).
- **Formatos:** JSON (metadados/API), PDF (íntegra → Markdown via
  `opendataloader_pdf`), SQLite/PostgreSQL (persistência), vetores `pgvector`.
- **Desafios já tratados:** captcha (OCR), deduplicação por chave
  `(numero_processo, tribunal, grau)`
  ([services.py:41-90](../apps/api/core/services.py#L41-L90)), normalização de grau,
  compressão `zlib` de movimentos/resultados.
- **Viabilidade de ML:** comprovada pela busca semântica em produção (embeddings
  locais em CPU, baixa latência) e pela extração estruturada via LLM.
- **Referência:** [docs/Especificacao_Dados_TRT6.md](./Especificacao_Dados_TRT6.md),
  [docs/Fluxo_End_to_End_Ingestao_API_Workers.md](./Fluxo_End_to_End_Ingestao_API_Workers.md).

---

### 3. Carregamento, EDA, tratamento e transformação

> *Reprodutibilidade e modularização do pipeline.*

**Cobertura: implementada diretamente no código (não em notebook).**

O carregamento, tratamento e transformação dos dados são feitos como código de
produção — modularizado em pacotes versionados, o que garante reprodutibilidade
real (qualquer execução parte das mesmas funções).

- **Carregamento:** comando `load_juristcu` ([README.md](../README.md))
  e providers de ingestão ([apps/ingestion/src/ingestion/providers.py](../apps/ingestion/src/ingestion/providers.py)).
- **Tratamento/limpeza/transformação:**
  - `mapear_processos` / normalização — [apps/ingestion/src/ingestion/utils.py](../apps/ingestion/src/ingestion/utils.py).
  - Deduplicação — `filtrar_processos_faltantes` ([services.py:41-90](../apps/api/core/services.py#L41-L90)).
  - **Encoding/representação:** texto canônico → embedding 384-d
    ([services.py:151-184](../apps/api/core/services.py#L151-L184),
    [embeddings.py](../shared/src/shared/embeddings.py)).
- **Modularização/reprodutibilidade:** o módulo `shared/` centraliza schemas,
  embeddings e clientes, importados por todos os serviços.

---

### 4. Modelo inicial simples + métricas em validação

> *KNN, regressão linear, árvore de decisão etc., com métricas em conjunto de validação.*

**Cobertura: conceitual — a busca já usa vizinhança por cosseno (estilo KNN).**

- **Baseline já em produção:** `buscar_processos_semanticos`
  ([services.py:241-255](../apps/api/core/services.py#L241-L255)) faz
  *nearest-neighbor* por cosseno sobre os embeddings — é, na prática, um KNN de
  recuperação.
- **Para o entregável formal de classificação:** treinar (direto no código) um
  modelo simples — ex.: Árvore de Decisão ou Regressão Logística — prevendo
  `resultado_reclamante` a partir das *features* estruturadas + embedding, com
  *split* treino/validação e *accuracy*/F1.

---

### 5. Dois modelos distintos comparados + visualizações

> *Matriz de confusão, ROC/AUC, gráficos de erro.*

**Cobertura: visualizações já prontas; comparação de modelos feita no código.**

- **Visualizações já implementadas** (não há lacuna de gráficos): o frontend tem
  os componentes de chart e os painéis que exibem as métricas/insights
  ([BaseChart.vue](../frontend/src/shared/components/ui/charts/BaseChart.vue),
  [InsightsPanel.vue](../frontend/src/pages/HomePage/components/InsightsPanel.vue)).
- **Comparação de modelos:** treinar e comparar ≥2 algoritmos (ex.: KNN vs.
  Árvore vs. Random Forest) diretamente no código de modelagem, com matriz de
  confusão e ROC/AUC sobre os mesmos *splits*.

---

### 6. Ajuste de hiperparâmetros (Grid/Random/Optuna)

**Cobertura: a executar no código de modelagem.**

- Hiperparâmetros já existentes no produto: `top_k` da busca
  ([views.py:163](../apps/api/core/views.py#L163)) e a escolha do modelo de
  embedding ([embeddings.py:21](../shared/src/shared/embeddings.py#L21)).
- Para o modelo de classificação: aplicar Grid/Random Search ou Optuna
  diretamente no código, registrando grade de parâmetros e resultados.

---

### 7. Validação cruzada + variância / over-underfitting + curvas de aprendizado

**Cobertura: a executar no código de modelagem.**

- Rodar k-fold (ou *stratified* k-fold, recomendado pelo desbalanceamento de
  classes), analisar a variância entre folds e gerar curvas de aprendizado —
  tudo no mesmo código de treino/avaliação.

---

### 8. Função de inferência / integração ao produto (endpoint)

> *Estrutura mínima de integração; pode ser um endpoint funcional.*

**Cobertura: completa — já há endpoints funcionais em produção.** ✅

- **Inferência de busca semântica:** `POST /api/processos/busca_semantica/`
  ([views.py:156-178](../apps/api/core/views.py#L156-L178)) → vetoriza a consulta
  e ranqueia por cosseno.
- **Função de inferência da LLM:** `analyze_file`
  ([worker-llm/main.py:90-91](../apps/worker-llm/main.py#L90-L91)) e a task Celery
  `run_pipeline` ([worker-llm/worker.py](../apps/worker-llm/worker.py)).
- **Geração de embedding na escrita:** `adicionar_analise_ao_processo`
  ([services.py:214-227](../apps/api/core/services.py#L214-L227)).
- **Consumo no produto:** o frontend chama a busca semântica
  ([useHomeSearch.ts](../frontend/src/pages/HomePage/composables/useHomeSearch.ts)).

> Para o modelo de classificação treinado, basta expor uma nova *action* no
> `ProcessoViewset` carregando o modelo serializado (`.pkl`/`joblib`).

---

### 9. Execução do pipeline completo com dados atualizados + estabilidade

**Cobertura: forte (pipeline de dados) + parcial (métricas do modelo).**

- **Pipeline end-to-end funcionando:** ingestão → API (dedup) → scraper+captcha →
  MinIO → worker-LLM → análise → embedding → busca, descrito e validado em
  [docs/Fluxo_End_to_End_Ingestao_API_Workers.md](./Fluxo_End_to_End_Ingestao_API_Workers.md#L250-L261).
- **Reprocessamento/atualização:** comandos `sincronizar_minio`,
  `atualizar_movimentos`, `indexar_vetores`
  ([apps/api/core/management/commands/](../apps/api/core/management/commands/)) e
  `reindexar_processos_sem_embedding` ([services.py:258-289](../apps/api/core/services.py#L258-L289)).
- **Notificação contínua:** [apps/search-notifier](../apps/search-notifier/README.md)
  reexecuta buscas salvas diariamente (evidência de operação estável).

> **Falta:** registrar as métricas finais do modelo de classificação e evidência
> de estabilidade (variância entre folds / execuções) — depende dos entregáveis 6–7.

---

### 10. Comunicação clara (relatório final)

**Cobertura: forte — documentação extensa já existe.**

- Definição do problema e pipeline: **este documento** + [docs/INDICE.md](./INDICE.md).
- Pipeline de dados e arquitetura: [docs/Arquitetura.md](./Arquitetura.md),
  [docs/Pipeline.md](./Pipeline.md), [docs/Mensageria.md](./Mensageria.md).
- Integração ao produto: seção 8 acima + [frontend/DESIGN.md](../frontend/DESIGN.md).

> **Falta:** consolidar, no relatório/apresentação final, os critérios de escolha
> do modelo e os resultados (saída dos entregáveis 5–7).

---

## Resumo do status

| # | Entregável | Status | Onde está / O que falta |
|---|---|---|---|
| 1 | Definição do problema de ML | 🟢 Completo | Definição formal redigida no README principal |
| 2 | Plano de dados + viabilidade | 🟢 Forte | Ingestão + DataJud + scraper + docs |
| 3 | Carregamento/EDA/tratamento | 🟢 No código | `load_juristcu`, `ingestion`, `services`, `embeddings` |
| 4 | Modelo inicial simples | 🟡 Parcial | KNN de busca pronto; falta classificador supervisionado |
| 5 | ≥2 modelos + visualizações | 🟡 Parcial | Gráficos prontos no frontend; falta comparar modelos no código |
| 6 | Ajuste de hiperparâmetros | 🟡 A fazer | A executar no código (Grid/Optuna) |
| 7 | Validação cruzada | 🟡 A fazer | A executar no código (stratified k-fold) |
| 8 | Inferência / endpoint | 🟢 Completo | `busca_semantica`, `analyze_file`, embeddings |
| 9 | Pipeline completo + estabilidade | 🟢/🟡 | Pipeline ok; faltam métricas do modelo |
| 10 | Comunicação | 🟢 Forte | Docs amplas; falta consolidar resultados de modelagem |

**O que falta para fechar a frente de modelagem (4, 5, 6, 7):** treinar o modelo
de classificação direto no código — (a) carregando os processos com análise do
banco, (b) usando `resultado_reclamante`/`desfecho` como alvo, (c) comparando ≥2
modelos com matriz de confusão e ROC/AUC, (d) fazendo tuning (Optuna/Grid) e (e)
validando com *stratified* k-fold — reaproveitando `montar_texto_indexacao` e
`embed_text` do módulo `shared`.
