# Fluxo End-to-End: Ingestao -> API -> Scraper -> LLM

Este documento descreve como o workspace esta organizado hoje e como o fluxo deve funcionar do ponto de vista operacional e de arquitetura.

## Objetivo

Validar o caminho completo do dado em quatro etapas:

1. `apps/ingestion` consulta a fonte de dados e prepara lotes.
2. A API Django recebe, deduplica e persiste os processos.
3. `apps/worker-scrapper/pje_scraper` resolve captcha, baixa a integra e envia o PDF para o bucket S3 local.
4. `apps/worker-llm` baixa o PDF do S3, extrai a analise e devolve o resultado para a API.

O fluxo nao e um acoplamento direto entre todos os servicos. Hoje ele e mediado por:

- HTTP entre ingestion e API.
- Celery entre scraper e LLM.
- MinIO como armazenamento temporario do PDF.
- PostgreSQL nao esta presente; a persistencia atual da API usa SQLite.

## Componentes do repositório

### `apps/ingestion`

Responsabilidade atual:

- Consultar a fonte de processos.
- Normalizar os campos com `mapear_processos`.
- Enviar lotes para `POST /api/processos/deduplicar/` por meio de `ProcessSubmitter`.
- Opcionalmente disparar o worker de captcha para processos pendentes de PDF com `--pending-pdf` e `--trigger`.

Entrypoint real:

- `uv run ingest`

### `apps/api`

Responsabilidade atual:

- Receber processos em `POST /api/processos/deduplicar/`.
- Remover duplicados e persistir o que falta.
- Listar processos sem PDF em `GET /api/processos/nao_possuem_pdf/`.
- Receber a analise final em `POST /api/processos/adicionar_analise/`.

Arquitetura observada:

- `core/views.py` expoe um `ProcessoViewset` com actions DRF.
- `core/services.py` concentra a logica de negocio.
- `core/serializers/` define os formatos de entrada e saida.

### `apps/worker-scrapper/pje_scraper`

Responsabilidade atual:

- Abrir o fluxo do PJe TRT-6.
- Selecionar o grau correto.
- Resolver captcha e obter `tokenCaptcha`.
- Baixar a integra em `fetch_with_token`.
- Salvar o PDF no bucket `pje-documents` no MinIO.
- Disparar a task do worker LLM com os metadados do processo e o nome do objeto.

Task Celery real:

- `worker_llm.run_pipeline`

### `apps/worker-llm`

Responsabilidade atual:

- Baixar o PDF do MinIO.
- Converter o PDF em texto.
- Rodar a analise com LLM.
- Enviar o payload final para `POST /api/processos/adicionar_analise/`.

Entrypoint real do pacote:

- `uv run llm-process`

## Contratos usados hoje

### Ingestion -> API

O ingestion envia uma lista de objetos com os campos esperados pelo serializer de deduplicacao.

Endpoint:

- `POST /api/processos/deduplicar/`

Proposito:

- Persistir apenas processos novos ou mais recentes.
- Retornar um resumo dos itens realmente gravados.

### API -> Scraper

Hoje a API nao chama o scraper diretamente. O disparo acontece pela camada de orquestracao do ingestion, em dois modos:

- `--trigger`: para cada processo retornado pelo ingestion, dispara `run_pipeline.delay(numero_processo, grau)`.
- `--pending-pdf`: consulta a API em `GET /api/processos/nao_possuem_pdf/` e dispara o scraper para os pendentes.

### Scraper -> MinIO -> LLM

O scraper grava o PDF em:

- bucket: `pje-documents`
- objeto: `{numero_processo}_{grau}.pdf`

Depois ele chama a task:

- `worker_llm.run_pipeline`

O LLM worker baixa esse objeto, analisa o PDF e faz um `POST` para:

- `POST /api/processos/adicionar_analise/`

### LLM -> API

Endpoint:

- `POST /api/processos/adicionar_analise/`

Proposito:

- Anexar os campos da analise ao processo correspondente.

## Sequencia recomendada para execucao local

### 1. Subir infraestrutura

O workspace usa `compose.yaml` para os servicos auxiliares:

- MinIO em `localhost:9000`.
- RabbitMQ em `localhost:5672`.

Comando:

```bash
docker compose up -d minio rabbitmq
```

### 2. Preparar a API

Na pasta da API:

```bash
cd apps/api
uv run python manage.py migrate
uv run python manage.py runserver 0.0.0.0:8000
```

### 3. Subir o worker de captcha

Na pasta do worker scraper:

```bash
cd apps/worker-scrapper
uv run celery -A pje_scraper.worker worker --loglevel=INFO
```

### 4. Subir o worker de LLM

Na pasta do worker LLM:

```bash
cd apps/worker-llm
uv run celery -A worker worker --loglevel=INFO
```

### 5. Rodar a ingestao

Na pasta da ingestao:

```bash
cd apps/ingestion
uv run ingest
```

Se o objetivo for disparar o captcha worker para os processos retornados, use:

```bash
uv run ingest --trigger
```

Se o objetivo for consultar a fila de processos sem PDF e reprocessar apenas eles, use:

```bash
uv run ingest --pending-pdf
```

## Como o fluxo deve se comportar

### Cenário principal

1. O ingestion obtém uma lista de processos da fonte configurada.
2. O ingestion envia esse lote para a API em `/api/processos/deduplicar/`.
3. A API persiste apenas os novos registros.
4. Para cada processo que precise da integra, o ingestion dispara a task do scraper ou consulta a lista de pendentes.
5. O scraper resolve o captcha do PJe TRT-6, baixa a integra e envia o PDF para o MinIO.
6. O scraper dispara a task do LLM worker com o bucket e o nome do objeto.
7. O LLM worker baixa o PDF, analisa o documento e envia a analise para a API.
8. A API anexa a analise ao processo em `/api/processos/adicionar_analise/`.

### Onde cada responsabilidade termina

- Ingestion termina quando o lote foi enviado e, se solicitado, os processos foram enfileirados para captura.
- Scraper termina quando o PDF foi salvo no bucket e a task do LLM foi disparada.
- LLM worker termina quando a analise foi enviada para a API.
- A API termina quando persistiu o lote ou a analise.

## Pontos de acoplamento atuais

Existem alguns pontos que valem ser tratados como contratos fixos do workspace:

- A API espera `DJANGO_SETTINGS_MODULE=api.settings`.
- O bucket do PDF no MinIO e `pje-documents`.
- O nome da task do worker LLM e `worker_llm.run_pipeline`.
- O captcha workflow depende de `x-grau-instancia` para o TRT-6.
- O LLM worker usa `WORKER_LLM_API_URL` para apontar para a API.

## Como validar o stack

### Testes unitarios

- `cd apps/api && uv run pytest`
- `cd apps/worker-scrapper && uv run pytest`
- `cd apps/worker-llm && uv run pytest`

### Verificacao de integracao local

1. Subir MinIO e RabbitMQ.
2. Subir a API com migrate.
3. Subir os dois workers.
4. Executar o ingestion com um provider local ou fixture.
5. Confirmar que o PDF foi enviado ao MinIO e que a analise voltou para a API.

### Sinais de que o fluxo esta funcionando

- A API responde em `http://localhost:8000/api/processos/deduplicar/`.
- O MinIO possui objetos no bucket `pje-documents`.
- O worker scraper mostra a task `worker_llm.run_pipeline` sendo disparada.
- O worker LLM mostra a chamada `POST /api/processos/adicionar_analise/`.

## Gaps conhecidos

- O worker LLM depende de um servidor de modelo acessivel pela variavel `WORKER_LLM_BASE_URL`.
- O fluxo completo ainda depende de acesso ao TRT-6 para o captcha e a integra.
- O frontend nao participa desse caminho.
- A orchestracao ainda esta distribuida entre scripts e tasks, nao em um unico serviço coordenador.

## Verificacao local realizada

O workspace foi testado com os servicos locais realmente subindo e respondendo:

- `docker compose up -d minio rabbitmq` iniciou os dois containers com sucesso.
- `cd apps/api && uv run python manage.py migrate` concluiu sem migracoes pendentes.
- `cd apps/api && uv run python manage.py runserver 0.0.0.0:8000` iniciou a API sem erros.
- `cd apps/worker-scrapper && uv run celery -A pje_scraper.worker worker --loglevel=INFO` conectou ao RabbitMQ e registrou a task `pje_scraper.worker.run_pipeline`.
- `cd apps/worker-llm && uv run celery -A worker worker --loglevel=INFO` conectou ao RabbitMQ e registrou a task `worker_llm.run_pipeline`.
- Um lote real do arquivo `apps/api/data/dataJud.json` foi convertido e enviado para `POST /api/processos/deduplicar/`, retornando `200` com o processo gravado.
- Depois da criacao do bucket `pje-documents` no MinIO, `GET /api/processos/nao_possuem_pdf/` passou a responder `200` com a lista de processos pendentes.

## Proxima evolucao sugerida

Se quisermos deixar esse fluxo mais robusto, o proximo passo seria criar um orquestrador explicito com contratos de fronteira entre ingestion, captcha e analise. Isso facilitaria:

- retries uniformes
- idempotencia
- melhor observabilidade
- testes de integracao mais previsiveis
