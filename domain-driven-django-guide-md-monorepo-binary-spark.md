# Plano: destravar o fluxo Celery ingestion → scrapper → worker-llm

## Contexto

Os 4 serviços Python (`api`, `ingestion`, `worker-scrapper`, `worker-llm`) já têm Dockerfiles e sobem via `compose.yaml`. RabbitMQ é o broker (hostname interno `rabbitmq`, AMQP em `:5672`). A `ingestion` publica `app.send_task("worker_scrapper.run_pipeline", ...)` em [apps/ingestion/src/ingestion/main.py:92](apps/ingestion/src/ingestion/main.py#L92) e [apps/ingestion/src/ingestion/main.py:124](apps/ingestion/src/ingestion/main.py#L124); o scrapper, ao concluir, publica `worker_llm.run_pipeline` em [apps/worker-scrapper/pje_scraper/worker.py:29](apps/worker-scrapper/pje_scraper/worker.py#L29). Apesar dos nomes baterem com os `@app.task(name=...)` registrados nos consumers, as tasks não chegam aos workers — porque o pipeline atual tem quatro defeitos somados que impedem o consumo das filas.

---

## Causa raiz (quatro defeitos somados)

### 1. Workers sobem sem importar os módulos que registram as tasks
[docker/entrypoints/celery.sh](docker/entrypoints/celery.sh) executa `celery -A shared.celery_client worker` — e o módulo [shared/src/shared/celery_client.py](shared/src/shared/celery_client.py) **não tem `include=` nem `autodiscover_tasks`**, nem importa os módulos `pje_scraper.worker` / `worker`. Resultado: o processo Celery não conhece nenhuma task. Se uma mensagem chegar, o worker loga `Received unregistered task of type 'worker_scrapper.run_pipeline'` e descarta.

### 2. `task_routes` usa nomes antigos
[shared/src/shared/celery_client.py:10-20](shared/src/shared/celery_client.py#L10-L20) roteia `"pje_scraper.worker.run_pipeline"` para `scrapper_queue`, mas o nome atual da task (vindo de `WORKER_SCRAPPER_TASK_NAME` em [shared/src/shared/constants.py:5](shared/src/shared/constants.py#L5)) é `"worker_scrapper.run_pipeline"`. Sem casamento de rota, a mensagem da ingestion cai na fila default `celery` em vez de `scrapper_queue`. (O bloco ainda está duplicado — atribuído duas vezes a `app.conf.task_routes`.)

### 3. `celery.sh` ignora a variável `QUEUE`
[apps/worker-scrapper/Dockerfile:59](apps/worker-scrapper/Dockerfile#L59) e [apps/worker-llm/Dockerfile:47](apps/worker-llm/Dockerfile#L47) exportam `ENV QUEUE=...`, mas o script [docker/entrypoints/celery.sh](docker/entrypoints/celery.sh) nunca passa `-Q "$QUEUE"` ao `celery worker`. Os workers escutam apenas a fila default `celery`, não `scrapper_queue` / `llm_queue`. Como consequência, mesmo se a rota fosse corrigida (defeito 2), as tasks roteadas para filas dedicadas ficariam sem consumidor.

### 4. `worker-llm` aponta callback HTTP para `localhost`
[apps/worker-llm/worker.py:12](apps/worker-llm/worker.py#L12) usa `DEFAULT_API_URL = "http://localhost:8000/..."`. Dentro do container, `localhost` é o próprio container — não a `api`. O `compose.yaml` define `WORKER_LLM_BASE_URL` mas **não** `WORKER_LLM_API_URL` (que é a variável realmente lida). Quando a task LLM rodar com sucesso e tentar fazer POST de volta, falha. Não bloqueia a entrega das tasks, mas quebra o final do fluxo — vou corrigir junto.

---

## Mudanças propostas

### A. `docker/entrypoints/celery.sh` — passar `-Q $QUEUE` e `--include $INCLUDE`

Reescrever para honrar duas envs novas:

```bash
#!/usr/bin/env bash
set -euo pipefail

CELERY_APP="${APP_MODULE}"
CMD="${CELERY_CMD:-worker}"
ARGS="${CELERY_ARGS:-}"

if [ -n "${QUEUE:-}" ]; then
  ARGS="$ARGS -Q $QUEUE"
fi
if [ -n "${INCLUDE:-}" ]; then
  ARGS="$ARGS --include=$INCLUDE"
fi

exec celery -A "$CELERY_APP" "$CMD" $ARGS
```

`--include` faz o Celery importar o módulo no boot, registrando o decorador `@app.task(...)` no `shared.celery_client.app`.

### B. `apps/worker-scrapper/Dockerfile` — declarar `INCLUDE`

Adicionar logo após `ENV QUEUE=scrapper_queue` (linha 59):

```dockerfile
ENV INCLUDE=pje_scraper.worker
```

Confirma o registro de [apps/worker-scrapper/pje_scraper/worker.py:14](apps/worker-scrapper/pje_scraper/worker.py#L14).

### C. `apps/worker-llm/Dockerfile` — declarar `INCLUDE`

Adicionar após `ENV QUEUE=llm_queue` (linha 47):

```dockerfile
ENV INCLUDE=worker
```

Como `worker.py` está no nível superior do pacote (declarado em [apps/worker-llm/pyproject.toml:25](apps/worker-llm/pyproject.toml#L25): `include = ["main*", "worker*", "convert*"]`), `--include=worker` o resolve.

### D. `shared/src/shared/celery_client.py` — rotas com nomes corretos, usar constantes

Substituir o arquivo inteiro por:

```python
import os

from celery import Celery

from shared.constants import WORKER_LLM_TASK_NAME, WORKER_SCRAPPER_TASK_NAME

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://user:password@localhost:5672//")

app = Celery("tasks", broker=BROKER_URL)

app.conf.task_routes = {
    WORKER_SCRAPPER_TASK_NAME: {"queue": "scrapper_queue"},
    WORKER_LLM_TASK_NAME: {"queue": "llm_queue"},
}
```

Resolve defeito 2 e elimina a duplicação do bloco.

### E. `apps/worker-llm/worker.py` — default da API

Trocar [linha 12](apps/worker-llm/worker.py#L12):

```python
DEFAULT_API_URL = "http://api:8000/api/processos/adicionar_analise/"
```

Mantém o override por `WORKER_LLM_API_URL` para uso fora do compose. Resolve defeito 4 sem precisar mexer no `compose.yaml`.

### F. (Opcional) `compose.yaml` — expor RabbitMQ ao host

Apenas se quiser inspecionar a UI de management (`localhost:15672`) de fora dos containers. Adicionar à entrada `rabbitmq`:

```yaml
    ports:
      - "5672:5672"
      - "15672:15672"
```

Não é necessário para o fluxo funcionar. Marcar como nice-to-have.

---

## Arquivos a modificar

| Arquivo | Motivo |
|---|---|
| [docker/entrypoints/celery.sh](docker/entrypoints/celery.sh) | passar `-Q`/`--include` |
| [apps/worker-scrapper/Dockerfile](apps/worker-scrapper/Dockerfile) | declarar `INCLUDE=pje_scraper.worker` |
| [apps/worker-llm/Dockerfile](apps/worker-llm/Dockerfile) | declarar `INCLUDE=worker` |
| [shared/src/shared/celery_client.py](shared/src/shared/celery_client.py) | corrigir `task_routes`, remover duplicação |
| [apps/worker-llm/worker.py](apps/worker-llm/worker.py) | default API URL apontando para `api:8000` |

Não há mudanças necessárias em `apps/ingestion/` (já usa o nome correto via constante) nem em `compose.yaml` (broker URL e `depends_on` já estão certos).

---

## Verificação (end-to-end)

Os passos abaixo precisam de Docker Desktop rodando. Eu (Claude) executarei e observarei os logs até as tasks fluírem corretamente.

1. **Rebuild só do necessário** (celery.sh, shared, scrapper, llm):
   ```bash
   docker compose build worker-scrapper worker-llm ingestion api
   ```

2. **Subir o stack**:
   ```bash
   docker compose up -d
   docker compose ps
   ```
   Esperado: 6 serviços `Up` (postgres, rabbitmq, minio, api healthy, worker-scrapper, worker-llm, ingestion).

3. **Confirmar que os consumidores assinaram as filas certas** (a fonte da verdade):
   ```bash
   docker compose exec rabbitmq rabbitmqctl list_queues name messages consumers
   ```
   Esperado:
   ```
   scrapper_queue  0  1   ← consumer pendurado = scrapper conectado
   llm_queue       0  1   ← consumer pendurado = worker-llm conectado
   celery          0  0   ← fila default vazia/sem consumer
   ```

4. **Confirmar nas filas que tasks estão sendo publicadas e drenadas**:
   ```bash
   docker compose logs ingestion | grep -E "Disparando worker|task_id"
   docker compose logs worker-scrapper | grep -E "Iniciando pipeline scraper|Task worker-llm disparada"
   docker compose logs worker-llm | grep -E "Iniciando task LLM|Analise enviada"
   ```

5. **Critério de parada** (atendido quando todos verdadeiros):
   - `list_queues` mostra `scrapper_queue` e `llm_queue` com `consumers >= 1` e `messages` oscilando (não acumulando indefinidamente).
   - `ingestion` registra ao menos uma linha "Disparando worker para processo …".
   - `worker-scrapper` registra "Iniciando pipeline scraper: numero=… grau=…" para esses processos.
   - `worker-scrapper` registra "Task worker-llm disparada: task_id=…".
   - `worker-llm` registra "Iniciando task LLM: task_id=…".
   - Nenhum log com `Received unregistered task` em qualquer worker.

6. **Diagnóstico se travar**:
   - `messages` crescendo em `celery` (fila default) ⇒ rota errada — re-checar mudança D.
   - `consumers = 0` em `scrapper_queue`/`llm_queue` ⇒ `-Q $QUEUE` não passou — re-checar celery.sh.
   - `Received unregistered task` ⇒ `--include` não pegou — checar `INCLUDE` no Dockerfile e WORKDIR.
   - `ConnectionRefused amqp://...localhost` em algum log ⇒ env `CELERY_BROKER_URL` não chegou ao processo; conferir `compose.yaml` `environment:`.
