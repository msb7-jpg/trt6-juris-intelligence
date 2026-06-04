# projetos6 — JurisTCU API

REST API built with Django + Django REST Framework exposing the [LeandroRibeiro/JurisTCU](https://huggingface.co/datasets/LeandroRibeiro/JurisTCU) dataset.

---

## Definição formal do problema de Machine Learning

> Mapeamento completo dos entregáveis da disciplina (Projetos 6 CC) em
> [docs/Requisitos_Projetos6_CC.md](docs/Requisitos_Projetos6_CC.md).

O produto coleta processos trabalhistas do **TRT-6 / DataJud (CNJ)**, extrai uma
análise estruturada da íntegra via LLM e gera embeddings para busca semântica.
Sobre esse acervo definimos **dois problemas de aprendizado de máquina**
complementares:

### Classificação supervisionada (modelo principal)

- **Tipo:** classificação multiclasse.
- **Variável-alvo:** `resultado_reclamante` ∈ {`ganhou`, `ganhou_parcial`,
  `perdeu`, `sem_decisao`}, definida em
  [resumo_ia.py](shared/src/shared/schemas/resumo_ia.py#L37-L41). Alvo
  alternativo: `desfecho` (7 classes).
- **Estrutura dos dados de entrada (features):** atributos relacionais do
  `Processo` — `classe`, `orgao_julgador`, `assuntos` (multirrótulo),
  `valor_causa`, `custas_valor_total` — combinados ao **embedding denso de 384
  dimensões** do texto canônico do processo (`montar_texto_indexacao` +
  `embed_text`). Cada amostra é um processo com análise concluída.
- **Métrica de avaliação:** **F1 macro** como métrica primária (as classes são
  desbalanceadas), acompanhada de *accuracy*, matriz de confusão e ROC/AUC
  (one-vs-rest) por classe.
- **Justificativa de valor:** estimar a chance de êxito do reclamante a partir
  das características iniciais do processo apoia advogados e partes na decisão de
  litigar ou acordar, e enriquece o ranqueamento da busca com um sinal preditivo
  de resultado provável.

### Recuperação semântica por similaridade (já em produção)

- **Tipo:** recuperação/ranqueamento não supervisionado (vizinhança por cosseno,
  estilo KNN).
- **Variável-alvo:** não há rótulo; o objetivo é ordenar processos por
  similaridade à consulta em linguagem natural.
- **Estrutura dos dados de entrada:** consulta textual do usuário → vetor de 384
  dimensões; base de embeddings dos processos em `pgvector`.
- **Métrica de avaliação:** similaridade de cosseno e precisão no top-k.
- **Justificativa de valor:** localizar jurisprudência relevante sem depender de
  correspondência exata de palavras. Implementado em
  `buscar_processos_semanticos` e exposto via
  `POST /api/processos/busca_semantica/`.

---

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (package manager)

---

## Project structure

```
projetos6/
├── api/                        # Django project
│   ├── api/                    # Settings, URLs, WSGI
│   │   ├── settings.py
│   │   └── urls.py
│   ├── core/                   # Main app
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── load_juristcu.py  # Custom management command
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── views.py
│   ├── juristcu.db             # SQLite database (created after loading)
│   └── manage.py
├── pyproject.toml
└── README.md
```

---

## Setup

### 1. Install uv

**Linux / macOS**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**via pip** (any platform)
```bash
pip install uv
```

After installing, restart your shell and verify:
```bash
uv --version
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Apply Django migrations

This creates the internal Django tables (auth, sessions, etc.) without touching the dataset tables.

```bash
cd api
python manage.py migrate
```

### 4. Load the dataset into SQLite

Downloads the dataset from HuggingFace and populates the `docs`, `qrels`, and `queries` tables.

```bash
python manage.py load_juristcu
```

Optional flags:

| Flag | Default | Description |
|---|---|---|
| `--repo` | `LeandroRibeiro/JurisTCU` | HuggingFace dataset repo |
| `--db` | settings `DATABASE` path | Override SQLite file path |
| `--if-exists` | `replace` | `replace` / `append` / `fail` |

Example with custom path:

```bash
python manage.py load_juristcu --db /tmp/custom.db --if-exists append
```

### 5. Run the development server

```bash
python manage.py runserver
```

---

## API endpoints

Base URL: `http://localhost:8000/api/`

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/documents/` | List all documents (paginated) |
| `GET` | `/api/documents/{key}/` | Get a single document |

### Filtering

Append any of these as query parameters:

```
/api/documents/?area=Licitações
/api/documents/?ano_acordao=2023
/api/documents/?colegiado=Plenário&tipo_processo=TC
/api/documents/?paradigmatico=S
```

Available filter fields: `key`, `num_acordao`, `ano_acordao`, `colegiado`, `area`, `tema`, `subtema`, `tipo_processo`, `tipo_recurso`, `autor_tese`, `paradigmatico`.
