# Busca Vetorial MVP

## Objetivo

Implementar uma busca semantica minima sem reestruturar o monorepo inteiro.

O MVP deve:

- receber uma consulta em linguagem natural
- retornar os 5 processos mais similares com score
- reaproveitar o pipeline ja existente de ingestao, scraping e analise
- evitar migracao imediata do banco relacional de SQLite para PostgreSQL

## Escolha tecnica minima

### Banco vetorial

Usar Qdrant em container separado.

Motivo:

- nao exige trocar o banco atual do Django
- integra bem com Python
- aceita payload junto do vetor
- simplifica o MVP em comparacao com migrar tudo para pgvector agora

### Embeddings

Usar `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` no backend.

Motivo:

- roda localmente em CPU
- suporta portugues de forma razoavel
- e suficiente para validar o fluxo end-to-end

Observacao:

Se o MVP funcionar, o modelo pode ser trocado depois por um embedding mais forte ou mais juridico sem mudar a API publica.

## Fluxo proposto

### 1. Ingestao

Mantem o fluxo atual:

- `apps/ingestion` consulta DataJud
- envia lote para `POST /api/processos/deduplicar/`
- API persiste processo e relacoes

### 2. Scraping

Mantem o fluxo atual com um passo a mais:

- `worker-scrapper` baixa a integra do PJe
- salva o PDF no MinIO
- dispara uma task do `worker-llm`

### 3. Analise estruturada

O `worker-llm` passa a:

- baixar o PDF do MinIO
- extrair texto
- gerar `ProcessoAnalise`
- chamar a API para salvar a analise do processo

### 4. Indexacao vetorial

Depois que a API receber a analise:

- monta um texto canonico para embedding
- gera embedding
- faz upsert do vetor no Qdrant usando o `Processo.id` como point id

### 5. Busca semantica

Novo endpoint da API:

- recebe `consulta`, `top_k` e filtros opcionais
- gera embedding da consulta
- busca no Qdrant
- usa os ids retornados para hidratar os dados no Django
- devolve itens prontos para o frontend com `similaridade`

### 6. Frontend

Substituir o mock atual por chamada real:

- `submitSearch` chama a API
- resultados e insights passam a vir do backend
- mocks podem ficar apenas como fallback de desenvolvimento, se desejado

## Texto a ser vetorizado

O embedding deve ser gerado a partir da concatenacao destes campos:

- `classe.nome`
- `orgao_julgador.nome`
- `assuntos[].nome`
- `analise.resumo`
- `analise.decisao`
- `analise.palavras_chave[]`
- `analise.desfecho`
- `analise.resultado_reclamante`

Formato sugerido:

```text
classe: Acao Trabalhista
orgao_julgador: 2a Vara do Trabalho de Recife
assuntos: horas extras; intervalo intrajornada
resumo: ...
decisao: ...
palavras_chave: ...
desfecho: sentenca_procedente
resultado_reclamante: ganhou
```

## Contrato minimo da API

### 1. Salvar analise e indexar

Endpoint sugerido:

`POST /api/processos/adicionar-analise/`

Payload minimo:

```json
{
  "numero_processo": "0000256-48.2025.5.06.0171",
  "grau": "1",
  "analise": {
    "resumo": "...",
    "decisao": "...",
    "palavras_chave": ["horas extras", "intervalo"],
    "status": "arquivado",
    "desfecho": "sentenca_procedente",
    "resultado_reclamante": "ganhou",
    "valor_causa": 31399.70,
    "custas_valor_total": 50.00
  }
}
```

Comportamento:

- localiza o processo por `numero_processo + tribunal + grau` ou por `numero_processo + grau`
- atualiza ou cria a analise
- indexa ou reindexa o processo no Qdrant

### 2. Buscar semanticamente

Endpoint sugerido:

`POST /api/processos/busca-semantica/`

Payload minimo:

```json
{
  "consulta": "trabalhei 12h sem intervalo e quero horas extras",
  "top_k": 5,
  "filtros": {
    "somente_procedentes": false,
    "orgao_contains": "recife",
    "data_ajuizamento_min": "2024-01-01"
  }
}
```

Resposta minima:

```json
{
  "items": [
    {
      "numero_processo": "0003987-21.2024.5.06.0007",
      "tribunal": "TRT6",
      "classe_nome": "Acao Trabalhista",
      "orgao_julgador_nome": "3a Turma",
      "data_ajuizamento": "2024-09-03",
      "resumo": "...",
      "decisao": "...",
      "palavras_chave": ["horas extras", "escala 12x36"],
      "desfecho": "sentenca_parcialmente_procedente",
      "resultado_reclamante": "ganhou_parcial",
      "valor_causa": 45800,
      "custas_valor_total": 916,
      "similaridade": 0.92
    }
  ]
}
```

## Arquivos para alterar

### Infra

- `compose.yaml`
  - adicionar servico `qdrant`
  - expor a porta `6333`
  - manter MinIO e RabbitMQ como estao

### Shared

- `shared/pyproject.toml`
  - adicionar `qdrant-client`
  - adicionar `sentence-transformers`

- `shared/src/shared/s3_client.py`
  - sem mudanca obrigatoria para busca vetorial

- `shared/src/shared/schemas/resumo_ia.py`
  - manter schema atual ou ajustar apenas se faltar campo relevante para indexacao

### API Django

- `apps/api/pyproject.toml`
  - garantir dependencia de `shared`
  - nenhuma dependencia vetorial precisa ficar aqui se tudo for encapsulado em `shared`

- `apps/api/api/urls.py`
  - manter o `ProcessoViewset`
  - nao precisa criar novo router para o MVP

- `apps/api/core/views.py`
  - adicionar action `adicionar_analise`
  - adicionar action `busca_semantica`

- `apps/api/core/services.py`
  - adicionar funcao para salvar analise no processo
  - adicionar funcao para montar documento de indexacao
  - adicionar funcao para indexar processo no Qdrant
  - adicionar funcao para buscar processos semanticamente

- `apps/api/core/serializers/processo_serializer.py`
  - possivelmente reutilizar no retorno da busca
  - pode exigir um serializer de leitura mais focado para a Home

### Worker Scrapper

- `apps/worker-scrapper/pje_scraper/worker.py`
  - apos upload no MinIO, disparar task do worker de LLM

### Worker LLM

- `apps/worker-llm/main.py`
  - manter como script manual de debug, se quiser

- `apps/worker-llm/pyproject.toml`
  - garantir `celery`, `requests` e `shared`

## Arquivos para criar

### Shared

- `shared/src/shared/embeddings.py`
  - carrega singleton do modelo de embedding
  - expoe `embed_text(text: str) -> list[float]`

- `shared/src/shared/vector_store.py`
  - cria cliente do Qdrant
  - garante criacao da collection
  - expoe `upsert_processo(...)` e `search_similar(...)`

### API Django

- `apps/api/core/serializers/busca_semantica_serializer.py`
  - serializer de entrada: `consulta`, `top_k`, `filtros`
  - serializer de saida: item com `similaridade`

- `apps/api/core/tests/views/test_processo_busca_semantica.py`
  - valida request vazio
  - valida retorno ordenado por score
  - valida filtros
  - mocka Qdrant para nao depender do servico real no teste

- `apps/api/core/tests/views/test_processo_adicionar_analise.py`
  - valida update ou create da analise
  - valida chamada de indexacao

### Worker LLM

- `apps/worker-llm/worker.py`
  - task Celery `run_llm_analysis(numero, grau, bucket, object_name)`
  - baixa PDF do MinIO
  - gera `ProcessoAnalise`
  - chama `POST /api/processos/adicionar-analise/`

### Frontend

- `frontend/src/shared/api/search.ts`
  - encapsula chamada para `/api/processos/busca-semantica/`

- `frontend/src/pages/HomePage/utils/mapApiCase.ts`
  - converte snake_case da API para camelCase do frontend

## Ordem recomendada de implementacao

1. Subir Qdrant em `compose.yaml`.
2. Criar `shared/src/shared/embeddings.py`.
3. Criar `shared/src/shared/vector_store.py`.
4. Implementar `POST /api/processos/adicionar-analise/`.
5. Acoplar a indexacao vetorial ao salvar analise.
6. Implementar `POST /api/processos/busca-semantica/`.
7. Criar task do `worker-llm` e encadear a partir do scraper.
8. Trocar o mock da Home por chamada real.

## O que nao entra no MVP

- migracao completa para PostgreSQL + pgvector
- recalculo em massa com versionamento de embedding
- reranking com cross-encoder
- painel de insights jurimetricos estatisticos completo
- filtros combinatorios complexos direto no vetor

## Criterio de pronto do MVP

- processo ingerido consegue chegar ate analise estruturada
- processo analisado gera vetor no Qdrant
- consulta retorna top 5 com score consistente
- frontend deixa de usar `MOCK_CASES` na Home
- testes de API passam sem depender de Qdrant real
