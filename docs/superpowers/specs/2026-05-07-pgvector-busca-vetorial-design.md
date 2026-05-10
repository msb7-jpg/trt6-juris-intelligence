---
title: Busca Vetorial (pgvector) para core_processo
date: 2026-05-07
tags: [spec, busca, pgvector, embeddings]
---

# Busca Vetorial (pgvector) para `core_processo`

## Objetivo

Adicionar **busca semantica** (vector search) sobre os processos presentes hoje em `apps/api/juristcu.db`, permitindo que o usuario envie um texto em linguagem natural (ex: "trabalhei 12h sem intervalo") e o sistema retorne os processos mais similares.

Escopo inicial:

- Indexar embeddings a partir de campos em `core_processo` (incluindo campos derivados do relacionamento `Processo -> Analise`).
- Armazenar **relacional + vetorial no mesmo banco** via **Postgres + pgvector**.
- Expor endpoint HTTP para consulta (`busca-semantica`) com filtros opcionais.

Fora de escopo (por agora):

- Indexar texto completo de PDF (chunking) via `pdf_url`.
- RAG / respostas geradas por LLM.
- Observabilidade e tuning avancado de recall/latencia alem do basico.

## Estado Atual (SQLite / Django)

O repositorio possui uma API Django (apps/api) usando SQLite (`ENGINE=sqlite3`). O arquivo local analisado foi:

- `apps/api/juristcu.db` (SQLite)

Tabelas relevantes (simplificado):

- `core_processo`: `numero_processo`, `tribunal`, `grau`, `data_ajuizamento`, `data_hora_ultima_atualizacao`, `pdf_url`, `classe_id`, `orgao_julgador_id`, `analise_id`
- `core_analise`: campos atuais incluem `resumo`, `decisao`, `status`, `desfecho`, `resultado_reclamante`, `valor_causa`, `custas_valor_total`. Esta spec assume a evolucao do schema para incluir `decisao_resumo`, `resumo_causa`, `palavras_chave_processo` e `palavras_chave_desfecho` (conforme payload do pipeline de analise).
- `core_palavrachave` e M2M `core_analise_palavras_chave`
- `core_assunto` e M2M `core_processo_assuntos`
- `core_classe`, `core_orgaojulgador`

Observacao: atualmente a base pode ter poucos registros com analise/resumos preenchidos (dependendo do ambiente). A arquitetura proposta considera que os resumos/keywords passarao a existir conforme o pipeline de analise roda.

## Arquitetura Proposta (Postgres + pgvector)

### Visao geral

1. Migrar a base de SQLite para **Postgres**.
2. Instalar a extensao **pgvector**.
3. Criar uma tabela para embeddings por processo.
4. Gerar embeddings offline (backfill) e manter atualizado quando `Analise`/keywords mudarem.
5. Criar endpoint de busca semantica que:
   - embedda a query do usuario
   - faz ANN search (HNSW) por similaridade
   - faz join para retornar dados do `core_processo`

### Modelo de embeddings

Provider/model escolhido (sem API key):

- `sentence-transformers` com `intfloat/multilingual-e5-small`
- Dimensao: **384** (logo, `vector(384)`)

Motivo:

- Boa qualidade e custo zero por request (rodando local)
- Funciona bem para PT-BR (multilingual)
- Leve o suficiente para CPU no MVP

### Texto a ser embedado (document representation)

Para cada `Processo`, concatenar em uma string deterministica com:

- `Analise.decisao_resumo` (principal)
- `Analise.resumo_causa` (principal)
- `Analise.palavras_chave_processo[].nome`
- `Analise.palavras_chave_desfecho[].nome`
- `Processo.classe.nome`

Formato sugerido (exemplo):

```text
DECISAO_RESUMO:\n<decisao_resumo>\n\nRESUMO_CAUSA:\n<resumo_causa>\n\nCLASSE:\n<classe>\n\nPALAVRAS_CHAVE_PROCESSO:\n- <kw_processo 1>\n- <kw_processo 2>\n\nPALAVRAS_CHAVE_DESFECHO:\n- <kw_desfecho 1>\n- <kw_desfecho 2>
```

Notas:

- Ordenar listas alfabeticamente para estabilidade.
- Persistir o texto final em banco para auditoria/reproducao.
- Usar um hash (ex: sha256) do `embedding_input` para idempotencia e para detectar quando precisa re-embedar.

Regra pratica para escolher campos:

- Embedding: texto narrativo e termos descritivos curtos (ex: resumos, tags).
- Filtros/metadados: campos categoricos e numericos (`tribunal`, `grau`, `status`, `desfecho`, `resultado_reclamante`, datas, `valor_causa`, `custas_*`).

### Armazenamento (tabela separada)

Criar tabela `core_processo_embedding` (um embedding por processo, versionavel via campos):

- `id` (PK)
- `processo_id` (FK `core_processo(id)`, UNIQUE)
- `embedding` (`vector(384)`)
- `embedding_model` (text) ex: `intfloat/multilingual-e5-small`
- `embedding_input` (text)
- `embedding_hash` (text, indexavel)
- `created_at`, `updated_at`

Racional:

- Evita inflar `core_processo`.
- Permite recomputar embeddings sem tocar no modelo principal.
- Permite evoluir para multiplas representacoes no futuro (ex: `type` ou `version`).

### Indexacao

Usar [pgvector](https://github.com/pgvector/pgvector) com [distancia cosseno](https://www.ibm.com/br-pt/think/topics/cosine-similarity).

SQL (referencia):

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- tabela
CREATE TABLE core_processo_embedding (
  id bigserial PRIMARY KEY,
  processo_id bigint NOT NULL UNIQUE REFERENCES core_processo(id) ON DELETE CASCADE,
  embedding vector(384) NOT NULL,
  embedding_model text NOT NULL,
  embedding_input text NOT NULL,
  embedding_hash text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- ANN index
CREATE INDEX core_processo_embedding_embedding_hnsw
  ON core_processo_embedding
  USING hnsw (embedding vector_cosine_ops);

-- filtros comuns podem virar indexes no relacional (exemplos)
CREATE INDEX core_processo_tribunal_idx ON core_processo(tribunal);
CREATE INDEX core_processo_grau_idx ON core_processo(grau);
```

Observacoes:

- Parametros do HNSW (`m`, `ef_construction`) podem ser tunados depois.
- Para bases pequenas, mesmo sem HNSW funciona; o index entra como caminho para crescer.

## API: Busca Semantica

### Endpoint

- `POST /api/processos/busca-semantica/`

Body (proposta):

```json
{
  "texto": "trabalho 12h sem intervalo",
  "k": 10,
  "filters": {
    "tribunal": "TRT6",
    "grau": "G1",
    "classe_codigo": "...",
    "assunto_codigo": 123
  }
}
```

Defaults:

- `k = 10`
- `filters` opcional

Resposta (proposta, resumo-only):

```json
[
  {
    "processo_id": 1,
    "numero_processo": "000...",
    "tribunal": "...",
    "grau": "G1",
    "classe": {"codigo": "...", "nome": "..."},
    "assuntos": [{"codigo": 123, "nome": "..."}],
    "resumo": "...",
    "similaridade": 0.82
  }
]
```

Semantica do score:

- Distancia cosseno do pgvector tipicamente retorna valores onde menor = mais proximo.
- Expor `similaridade` como numero normalizado (ex: `1 - distance`) para UX.

### Query SQL (referencia)

```sql
SELECT
  e.processo_id,
  (1 - (e.embedding <=> $1::vector)) AS similarity
FROM core_processo_embedding e
JOIN core_processo p ON p.id = e.processo_id
WHERE
  ($2::text IS NULL OR p.tribunal = $2)
  AND ($3::text IS NULL OR p.grau = $3)
ORDER BY e.embedding <=> $1::vector
LIMIT $4;
```

Filtros adicionais (classe/assuntos) serao aplicados no join (possivelmente com `EXISTS` para M2M).

Notas de compatibilidade de filtros:

- No schema atual, `Processo.grau` e um `CharField` (ex: "G1" ou "G2"). O endpoint deve documentar e normalizar entradas tipo "1"/"2" se isso for desejado.
- `classe_codigo` refere-se a `core_classe.codigo`.
- `assunto_codigo` refere-se a `core_assunto.codigo` (nao ao `id`).

## Pipeline de Geracao e Atualizacao de Embeddings

### Backfill

Adicionar um management command (ex: `python manage.py backfill_embeddings`) que:

1. Itera `core_processo`.
2. Monta `embedding_input` (resumo + keywords-like fields).
3. Calcula `embedding_hash`.
4. Se nao existir embedding ou hash mudou: gera embedding e faz upsert.

### Atualizacao incremental

Quando `adicionar_analise` rodar, recomputar embedding do processo afetado.

No MVP pode ser sincrono (mesma request) se latencia for aceitavel. Se nao, evoluir para async usando a infra ja existente (Celery + RabbitMQ).

## Migracao SQLite -> Postgres

Proposta minima:

1. Subir Postgres (docker) e habilitar `pgvector`.
2. Alterar `DATABASES` do Django para Postgres.
3. Rodar `migrate` para criar o schema.
4. Fazer import dos dados atuais do SQLite para Postgres (one-shot) via:
   - `dumpdata/loaddata` (Django) ou
   - `sqlite3 .dump` + adaptacao, ou
   - script Python que leia SQLite e escreva via ORM.

Recomendacao para este repo:

- Usar **script Python** (le SQLite e escreve via ORM) para manter integridade de FKs/M2M e permitir re-runs idempotentes.

Como este repo ja esta evoluindo para um stack Docker, a opcao Docker + Postgres tende a encaixar melhor.

## Riscos e Decisoes

- **Dados faltantes de `Analise.decisao_resumo` / `Analise.resumo_causa`**: sem esses textos, embeddings nao existem. Mitigacao: permitir fallback (nao indexar) e retornar vazio/erro claro; garantir pipeline de analise.
- **Qualidade de embeddings PT-BR juridico**: `multilingual-e5-small` e bom baseline, mas pode precisar de modelo mais forte/ajuste. Guardar `embedding_model`/`embedding_input` permite reprocessar.
- **Custo/latencia**: embeddings locais em CPU podem ser lentos em lote grande. Mitigacao: backfill offline, batch, e/ou GPU.

## Checklist de Implementacao (alto nivel)

- Postgres + pgvector no ambiente (compose)
- Migracao Django para Postgres
- Modelo/tabela `core_processo_embedding`
- Gerador de embedding (sentence-transformers)
- Command de backfill
- Endpoint `busca-semantica` com filtros
- Testes: construcao do texto + endpoint (com embedding stub)
