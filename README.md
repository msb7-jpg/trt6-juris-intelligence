# JusTRT6 — Labor Jurisprudence Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20.svg)](https://www.djangoproject.com/)
[![Vue](https://img.shields.io/badge/Vue.js-3.5-4FC08D.svg)](https://vuejs.org/)
[![pgvector](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end legal intelligence platform for the **TRT-6** (Tribunal Regional do Trabalho da 6ª Região). It ingests official labor court lawsuits from CNJ DataJud, resolves PJe captchas automatically to fetch full procedural case files, structures rulings and claim outcomes using local LLMs, and powers 384-dimensional vector semantic search with an interactive Vue 3 dashboard.

---

## ⚡ Highlights & Impact

- **End-to-End Automated Pipeline**: Eliminates manual case collection across DataJud and PJe portals.
- **Autonomous PJe Scraping**: Integrated Playwright browser automation coupled with local OCR (`ddddocr`) solves procedural captchas and downloads full PDF dockets without recurring captcha API costs.
- **Structured Legal Extraction**: Local LLM worker (OpenAI-compatible / LM Studio) extracts core judicial acts, outcomes (`ganhou`, `perdeu`, `acordo`), case amounts, court costs, and legal summaries directly conforming to strict Pydantic schemas.
- **Sub-Second Vector Search**: PostgreSQL with `pgvector` and `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) performs cosine similarity search across indexed labor precedents.
- **Modern Interactive UI**: High-density Vue 3 + Vite dashboard featuring semantic search, predictive outcome indicators, and case analytics.

---

## 🖥️ Interactive Preview

| Semantic Search & Discovery | Case Details & Extracted Insights |
| :---: | :---: |
| ![JusTRT6 Semantic Search](docs/assets/pagina-inicial-solucao.gif) | ![Case Details & Judicial Insights](docs/assets/pagina-detalhes-solucao.gif) |

---

## 🏗️ System Architecture

![JusTRT6 Architecture & Event Flow](docs/assets/flow.gif)

The platform is designed as an asynchronous microservices pipeline:
1. **Data Ingestion**: Batches are fetched from CNJ DataJud API, normalized, and deduplicated in PostgreSQL.
2. **Autonomous Docket Scraping**: Processes missing documents trigger Celery tasks to solve PJe captchas via Playwright + `ddddocr`, uploading docket PDFs to MinIO.
3. **LLM Extraction**: `worker-llm` extracts full-text markdown from PDFs, prompts a local LLM (e.g. Gemma / LM Studio) for structured JSON analysis conforming to Pydantic schemas.
4. **Vector Embedding & Indexing**: Judicial summaries are embedded using `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions) and indexed directly into PostgreSQL via `pgvector`.
5. **Interactive UI**: Vue 3 dashboard performs sub-second cosine distance searches and displays predictive legal insights.

---

## 📦 Workspace Structure

The project is managed as a unified [uv](https://github.com/astral-sh/uv) workspace:

```
.
├── apps/
│   ├── api/              # Django 5 + Django REST Framework + pgvector service
│   ├── ingestion/        # DataJud batch ingestion client and normalizer
│   ├── worker-scrapper/  # Playwright + ddddocr scraper for PJe TRT-6
│   └── worker-llm/       # LLM docket parser using OpenDataDataLoader & LangChain
├── frontend/             # Vue 3, Vite, Tailwind/CSS variables, Pinia, Vue Query
├── shared/               # Shared models, S3/MinIO client, Celery client, and embeddings
├── notebooks/            # Exploratory data analysis & 2D UMAP embedding cluster plots
├── scripts/              # Validation benchmark scripts (MLflow experiment tracking)
├── docs/assets/          # Product screenshots, animated flows, and research charts
├── compose.yaml          # Multi-container orchestration (Postgres, RabbitMQ, MinIO, workers)
└── pyproject.toml        # Root uv workspace configuration
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+**
- **[uv](https://github.com/astral-sh/uv)** package manager
- **[Docker](https://www.docker.com/)** and **Docker Compose**
- **Node.js 20+** or **[Bun](https://bun.sh/)** (for frontend)

### 1. Clone & Environment Configuration

```bash
git clone https://github.com/MigueldsBatista/trt6-juris-intelligence.git
cd trt6-juris-intelligence

# Copy sample environment variables
cp .env.example .env
```

### 2. Launch Infrastructure Services

Start PostgreSQL with pgvector, RabbitMQ, and MinIO:

```bash
docker compose up -d postgres rabbitmq minio
```

Default credentials:
- **PostgreSQL**: `localhost:5432` (db: `trt6`, user: `trt6`, password: `trt6`)
- **RabbitMQ Management**: `http://localhost:15672` (user: `user`, password: `password`)
- **MinIO Console**: `http://localhost:9001` (user: `minioadmin`, password: `minioadmin`)

### 3. Backend & Workspace Setup

Install dependencies across all workspace packages:

```bash
uv sync
```

Apply database migrations:

```bash
cd apps/api
uv run python manage.py migrate
cd ../..
```

Install Playwright browser binaries (for the scraper):

```bash
uv run playwright install chromium
```

### 4. Run the Platform

#### Running via Docker Compose (Recommended)

```bash
docker compose up --build
```

#### Running Locally for Development

In separate terminal sessions:

```bash
# 1. Start Django API
cd apps/api && uv run python manage.py runserver 0.0.0.0:8000

# 2. Start Scraping Worker
uv run celery -A pje_scraper.worker worker --loglevel=INFO

# 3. Start LLM Analysis Worker
cd apps/worker-llm && uv run celery -A worker worker --loglevel=INFO

# 4. Start Frontend
cd frontend && bun install && bun dev
```

---

## 🔌 API Endpoints Reference

Base URL: `http://localhost:8000/api/`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/processos/deduplicar/` | Ingests and deduplicates processes from DataJud |
| `GET` | `/api/processos/nao_possuem_pdf/` | Lists processes pending docket download |
| `GET` | `/api/processos/nao_possuem_analise/` | Lists processes pending LLM legal analysis |
| `POST` | `/api/processos/adicionar_analise/` | Receives structured LLM output and indexes embeddings |
| `POST` | `/api/processos/busca_semantica/` | 384-dimensional cosine similarity semantic search |
| `GET` | `/health/` | Service health status |

### Semantic Search Example

```bash
curl -X POST http://localhost:8000/api/processos/busca_semantica/ \
  -H "Content-Type: application/json" \
  -d '{
    "consulta": "horas extras não pagas e intervalo intrajornada suprimido",
    "top_k": 5
  }'
```

---

## 🧪 Testing & Code Quality

Run tests across workspaces:

```bash
# Test API
cd apps/api && uv run pytest

# Test scraper worker
cd apps/worker-scrapper && uv run pytest

# Test LLM worker
cd apps/worker-llm && uv run pytest
```

Lint and formatting check:

```bash
uv run ruff check .
```

---

## 📊 Machine Learning Evaluation & Empirical Insights

### 1. High-Dimensional Embedding Interpretability (UMAP)
Using 2D UMAP projection on 384-dimensional dense vectors generated by `paraphrase-multilingual-MiniLM-L12-v2`, lawsuits naturally cluster according to legal outcome (`ganhou`, `perdeu`, `acordo`, `sem_decisao`):

<p align="center">
  <img src="docs/assets/clusters_processos_juridicos.png" alt="2D UMAP Clusters of Legal Precedents" width="750"/>
</p>

### 2. Statistical Distributions & Jurimetrics

| Outcome Distribution (`resultado_reclamante`) | Claim Value Log Distribution (`valor_causa_log`) |
| :---: | :---: |
| ![Outcome Distribution](docs/assets/distribuicao_resultado_reclamante.png) | ![Case Value Distribution](docs/assets/distribuicao_valor_causa.png) |

### 3. Search Quality Benchmark (MLflow)
We benchmark query latency and retrieval accuracy using a curated Golden Set with MLflow tracking:

```bash
# Run search benchmark evaluation
uv run python scripts/validate_search.py

# Launch MLflow Tracking UI
uv run mlflow ui
```

<p align="center">
  <img src="docs/assets/experimentos_ml.png" alt="MLflow Search Evaluation Dashboard" width="750"/>
</p>

Key observed metrics:
- **Average Vector Retrieval Latency (`avg_latency_ms`)**: ~26.3 ms on PostgreSQL + pgvector
- **Dense Vector Representation**: 384 dimensions (`MiniLM-L12-v2`)

---

## 📚 Academic Research & Paper

This project was developed at **CESAR School** (Recife, Brazil) as an applied legal intelligence system:

> **JusTRT6 Search: Uma Solução de Busca Semântica e Análise Jurídica Baseada em Embeddings para Apoio à Tomada de Decisão**  
> *Beatriz Pereira, Matheus Velame, Miguel Batista, Rafael Andrade, Rafaela Vidal, Tiago Gurgel*  
> 📄 Full Paper: [`machine-learning/jusTRT6-artigo-final.pdf`](machine-learning/jusTRT6-artigo-final.pdf)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
