# JusTRT6 / SecureAI Lab — Cibersegurança Aplicada a Dados e IA (Partes 1 e 2)

> **Branch:** `feat/ciberseguranca-parte1-e-2`  
> **Disciplina:** Cibersegurança Aplicada a Dados e IA — CESAR School (Prof. Renatta Nigro)  
> **Relatório Técnico Final (PDF):** [docs/Projeto2_Relatorio_Ciberseguranca.pdf](docs/Projeto2_Relatorio_Ciberseguranca.pdf)

Este repositório reúne a **implementação completa, os experimentos reais, as capturas da aplicação em funcionamento e o relatório técnico em PDF** para a entrega de **Cibersegurança (Partes 1 e 2)**. Este `README.md` foi estruturado como **guia completo de apresentação e referência técnica**.

---

## 1. Documentos e Entregáveis Principais

| Documento | Finalidade | Link |
| :--- | :--- | :--- |
| **Relatório Final (PDF — 9 páginas)** | Documento formatado em Pandoc + Eisvogel + XeLaTeX com capa, sumário, métricas reais e screenshots | [docs/Projeto2_Relatorio_Ciberseguranca.pdf](docs/Projeto2_Relatorio_Ciberseguranca.pdf) |
| **Fonte do Relatório** | Markdown com frontmatter Eisvogel e imagens embutidas | [docs/projeto2_relatorio_final.md](docs/projeto2_relatorio_final.md) |
| **Resultados Brutos dos Experimentos** | Saída automática gerada por `scripts/run_projeto2_experiments.py` | [docs/projeto2_relatorio_resultados.md](docs/projeto2_relatorio_resultados.md) |
| **Especificação & Arquitetura (Projeto 2)** | Mapeamento formal dos requisitos de `Aula 26 - Projeto 2.pdf` | [docs/projeto2_requisitos_e_arquitetura.md](docs/projeto2_requisitos_e_arquitetura.md) |
| **Otimização Docker + `uv`** | Histórico das otimizações de imagem (`pytorch-cpu`, `--no-dev`, desacoplamento do `shared`) | [docs/docker_uv_optimization_plan.md](docs/docker_uv_optimization_plan.md) |
| **Documentação Parte 1 (SecureAI Lab)** | Plano e relatório base da etapa 1 | [PLANO_ADEQUACAO_SEGURANCA.md](PLANO_ADEQUACAO_SEGURANCA.md) / [Relatório Projeto - SecureAI Lab - Cibersegurança.md](Relatório%20Projeto%20-%20SecureAI%20Lab%20-%20Cibersegurança.md) |

---

## 2. Contexto: O que já existia vs. O que foi construído vs. O que é simulado

O **JusTRT6** já existia como uma plataforma de inteligência jurídica (Django/DRF, PostgreSQL com `pgvector`, MinIO S3, RabbitMQ/Celery e frontend Vue 3). Para não reescrever a plataforma nem inflar a infraestrutura com serviços desnecessários, **reutilizamos a stack existente** e construímos sobre ela o módulo de cibersegurança (`/api/security/` e `/seguranca`):

| Camada / Funcionalidade | Origem | Propósito (`Evitar` / `Detectar` / `Simular`) | Como funciona na prática |
| :--- | :--- | :--- | :--- |
| **Token Auth (`/api/auth/*`), PostgreSQL, MinIO, Vue 3 + ApexCharts** | **Nativo da aplicação** | Base operacional | Autenticação por token, banco relacional, storage S3 e biblioteca de gráficos já faziam parte do sistema. |
| **Hooks de Auditoria no Login (`AUTH_SUCCESS` / `AUTH_FAILURE`)** | **Integrado ao fluxo nativo** | **Detectar** tentativas reais de acesso indevido | `LoginView` em [apps/api/core/views.py](apps/api/core/views.py) registra cada tentativa (sucesso ou falha), ator e IP na tabela `SecurityEvent`. |
| **Derivação Dinâmica de Chaves (`PBKDF2-HMAC-SHA256`)** | **Construído (Proteção real)** | **Evitar** chaves fixas e reutilização de cifra | Gera `salt` (16B) e `nonce` (8B) aleatórios via `os.urandom` a cada operação (100.000 iterações). Mesmo texto + mesmo segredo nunca geram o mesmo ciphertext. |
| **Cifra `SPN Customizada` + `AES-256-GCM`** | **Construído (Proteção + Estudo)** | **Evitar** exposição de dados e **demonstrar** XOR, S-Box, P-Box, blocos, confusão e difusão | `DynamicSPNCipher` (128 bits, 8 rodadas, CBC) implementa explicitamente os operadores exigidos na Parte 2; `AES-256-GCM` atende à arquitetura de referência da Parte 5. |
| **Esteganografia LSB em PNG + Digest `SHA-256`** | **Construído (Proteção real)** | **Evitar** percepção visual do dado cifrado e **impedir** uso de arquivo adulterado | Oculta o payload cifrado nos bits menos significativos (LSB) do PNG com cabeçalho `JTCU` + `SHA-256`. Qualquer alteração de 1 byte aborta a extração (`HTTP 400`) e registra `FILE_TAMPERED`. |
| **Simulação de Adulteração (1 byte)** | **Simulado (Ambiente controlado)** | **Testar** a barreira de integridade | Botão *Simular Adulteração* no dashboard e passo no script de experimento alteram 1 byte do PNG para provar o bloqueio imediato e o registro do incidente. |
| **Ataques (Força Bruta, Diferencial/Avalanche, Estatístico)** | **Simulado (Ambiente controlado)** | **Avaliar** a resistência matemática do sistema | Força bruta ataca um **espaço reduzido (12 bits)** para medir o throughput real (`chaves/s`) e calcular a inviabilidade em 128/256 bits. Diferencial e estatístico medem Avalanche, Entropia de Shannon e $\chi^2$. |
| **Carga Experimental Big Data (2k–5k eventos)** | **Simulado + Eventos reais** | **Validar** volume e treinar/testar a IA | `generate_experimental_events` insere em lote (`bulk_create`) milhares de eventos normais + 3 perfis anômalos sintéticos, além dos eventos reais gerados pela API, salvando snapshot JSON no MinIO. |
| **IA Detecção de Anomalias (`IsolationForest`)** | **Construído (Detecção real)** | **Detectar** comportamentos anormais | Extrai 6 métricas por ator a partir de `SecurityEvent` e executa `IsolationForest` (`scikit-learn`), gravando alertas em `AnomalyAlert`. |

---

## 3. Conceitos Fundamentais (Base para Explicação na Apresentação)

### 3.1 Criptografia Simétrica, Chave Dinâmica, Confusão e Difusão
- **Por que a chave não pode ser fixa?** Se a mesma chave for usada diretamente em todo bloco/mensagem, padrões do texto claro vazam e ataques de dicionário/rainbow tables se tornam viáveis. Com `PBKDF2-HMAC-SHA256` + `salt` (16B) + `nonce` (8B) aleatórios por operação, a chave derivada muda a cada cifragem e influencia todas as rodadas via subchaves `HMAC-SHA256`.
- **Confusão (Shannon):** Esconder a relação entre a chave e o texto cifrado. Na `DynamicSPNCipher`, isso é feito pela **S-Box** (substituição não linear bijetiva de 256 bytes) + mistura **XOR** com a subchave da rodada.
- **Difusão (Shannon):** Espalhar a influência de 1 único bit do texto claro ou da chave por todo o texto cifrado. Na `DynamicSPNCipher`, isso é feito pela **P-Box** (permutação de posições), pelo passo `_diffuse_block` (rotação e XOR entre bytes adjacentes) e pelo encadeamento **CBC** com `IV` aleatório de 16 bytes.
- **Por que comparar `SPN Customizada` vs. `AES-256-GCM`?**
  - A `SPN Customizada` (CBC) obteve **51,13%** de efeito avalanche ao alterar 1 bit do texto claro e **50,35%** ao alterar 1 bit da chave (ideal teórico: ~50%).
  - O `AES-256-GCM` usa internamente **AES-CTR** (cifra de fluxo) + tag **GHASH**: alterar 1 bit no texto claro altera apenas 1 bit correspondente no ciphertext + ~50% da tag de 16 bytes (resultando em **4,35%** no texto, mas **49,92%** ao alterar 1 bit da **chave**). Essa diferença é um excelente ponto técnico para destacar na apresentação.

### 3.2 Criptografia vs. Esteganografia vs. Integridade (`SHA-256`)
- **Criptografia** garante **confidencialidade** (o conteúdo existe, mas é ilegível sem a chave).
- **Esteganografia (LSB)** garante **ocultação** (esconde que há uma mensagem secreta dentro de uma imagem PNG aparentemente comum, alterando apenas o bit menos significativo de cada canal RGB — variação máxima de $\pm 1$ em 255, imperceptível ao olho humano).
- **Função Hash (`SHA-256`)** garante **integridade**: antes de embutir o payload, gravamos o cabeçalho `JTCU` + tamanho (4B) + `SHA-256` (32B). Se 1 único byte da imagem for adulterado, o hash não bate na extração e o sistema bloqueia o dado.

### 3.3 Os 3 Ataques Controlados e Métricas de Avaliação
1. **Força Bruta:** Como testar $2^{128}$ ou $2^{256}$ chaves é fisicamente impossível, simulamos a quebra em um **espaço reduzido de 12 bits** ($4.096$ chaves — quebrado em **873 tentativas**) para medir a velocidade real do algoritmo no hardware atual (**~2.938–4.590 chaves/s**) e calcular o tempo médio para quebrar o espaço completo ($2^{127}$ ou $2^{255}$ tentativas $\rightarrow$ $10^{27}$ a $10^{65}$ anos).
2. **Ataque Diferencial (Efeito Avalanche):** Altera exatamente **1 bit** na entrada (texto claro ou chave), cifra ambos com os mesmos parâmetros e mede a **Distância de Hamming** (% de bits diferentes na saída). Um algoritmo seguro deve ficar próximo a **50%**.
3. **Ataque Estatístico:** Analisa a distribuição de bytes da saída cifrada:
   - **Entropia de Shannon:** Mede a aleatoriedade (máximo teórico = **8,0 bits/byte**; medimos **7,34–7,36 bits/byte** na amostra).
   - **Teste Qui-Quadrado ($\chi^2$):** Verifica se há viés estatístico ou concentração de caracteres/bytes.

### 3.4 Big Data e Inteligência Artificial (`IsolationForest`)
- **Por que `IsolationForest`?** É um algoritmo não supervisionado ideal para segurança porque **não exige um dataset previamente rotulado de ataques**: ele isola observações raras/anômalas com poucas divisões em árvores aleatórias.
- **Quais features a IA analisa?** Para cada ator (`actor_label`), agregamos no PostgreSQL:
  1. `total_events` (volume total de eventos)
  2. `auth_failures` (falhas de login)
  3. `decrypt_failures` (falhas de descriptografia)
  4. `file_tampered` (violações de hash/integridade)
  5. `atypical_hours` (acessos entre 00h e 06h)
  6. `avg_latency` (latência média das operações)
- **Mapeamento para os 5 tipos de anomalias do PDF:** `AUTH_BRUTE_FORCE`, `HIGH_DECRYPT_FAIL_RATE`, `FILE_ALTERATION`, `ATYPICAL_ACCESS_PATTERN` e `EVENT_BURST`.

---

## 4. O que foi feito exatamente nesta entrega

### A. Otimizações Docker, `uv` e Desacoplamento do `shared`
- **Desacoplamento (`shared/`):** Movidos `embeddings.py` e `formatters/currency.py` para `apps/api/core/`, e `llm_constants.py` para `apps/worker-llm/constants.py`; removidos `boto3` e `sentence-transformers` de [shared/pyproject.toml](shared/pyproject.toml).
- **PyTorch CPU & Limpeza (`pyproject.toml` e `apps/api/pyproject.toml`):** Roteamento de `torch`/`torchvision` para `https://download.pytorch.org/whl/cpu` (eliminando ~4,6 GB de CUDA/Triton), remoção de dependências mortas (`datasets`, `hf`, `pandas`, `pypdf`, `tabulate`) e separação de `[dependency-groups].dev`.
- **Docker Multi-stage:** `--no-dev` nos 5 Dockerfiles e cache mount `--mount=type=cache,target=/root/.cache/uv`. Resultado medido: imagem `juristcu-api:latest` com **467 MB** compactada (`2.18 GB` descompactada) e rebuild incremental de código em **2.9s**.
- **MinIO compatível:** Atualizado `compose.yaml` para `cgr.dev/chainguard/minio:latest`.

### B. Backend de Segurança (`apps/api/core/`)
- [apps/api/core/security/cipher.py](apps/api/core/security/cipher.py): `derive_dynamic_key`, `DynamicSPNCipher`, `encrypt_data`, `decrypt_data`.
- [apps/api/core/security/steganography.py](apps/api/core/security/steganography.py): `create_cover_png`, `embed_payload_in_png`, `extract_payload_from_png`.
- [apps/api/core/security/attacks.py](apps/api/core/security/attacks.py): `run_brute_force_attack`, `run_differential_attack`, `run_statistical_attack`, `evaluate_security_suite`.
- [apps/api/core/security/anomaly_detector.py](apps/api/core/security/anomaly_detector.py): `record_security_event`, `generate_experimental_events`, `detect_anomalies`.
- [apps/api/core/models/security_events.py](apps/api/core/models/security_events.py) + [0009_security_events_and_anomalies.py](apps/api/core/migrations/0009_security_events_and_anomalies.py): `SecurityEvent`, `AnomalyAlert`, `AttackExperiment`.
- [apps/api/core/security/views.py](apps/api/core/security/views.py) + [apps/api/api/urls.py](apps/api/api/urls.py): endpoints `/api/security/encrypt/`, `/decrypt/`, `/steganography/embed/`, `/steganography/extract/`, `/attacks/run/`, `/bigdata/simulate/`, `/ai/detect-anomalies/` e `/dashboard/`.

### C. Frontend (`/seguranca`)
- [frontend/src/pages/SecurityDashboardPage/SecurityDashboardPage.vue](frontend/src/pages/SecurityDashboardPage/SecurityDashboardPage.vue) e [frontend/src/services/security.ts](frontend/src/services/security.ts): laboratório interativo completo com gráficos `vue3-apexcharts`, upload/download de PNG customizado e botão **Simular Adulteração**.

### D. Testes, Automação e Relatório PDF
- [apps/api/core/tests/test_security_projeto2.py](apps/api/core/tests/test_security_projeto2.py): **5/5 testes unitários aprovados**.
- [scripts/run_projeto2_experiments.py](scripts/run_projeto2_experiments.py): executa toda a bateria contra a API ativa e gera os resultados experimentais.
- [docs/Projeto2_Relatorio_Ciberseguranca.pdf](docs/Projeto2_Relatorio_Ciberseguranca.pdf): relatório compilado com `pandoc` + `eisvogel.latex` + `xelatex` com capturas reais em `docs/assets/projeto2/`.

---

## 5. Checklist de Rastreabilidade (`Aula 26 - Projeto 2.pdf` $\rightarrow$ Código)

| Página | Trecho / Requisito do PDF | Onde é cumprido no código | Status |
| :---: | :--- | :--- | :---: |
| **Pág. 3 / Pág. 7** | *"Desenvolver um mecanismo de criptografia simétrica com geração dinâmica de chaves"* / *"Chave secreta: Deve influenciar a cifragem; Não pode ser fixa"* | `derive_dynamic_key` (`PBKDF2-HMAC-SHA256` com `salt` 16B e `nonce` 8B aleatórios) em [apps/api/core/security/cipher.py](apps/api/core/security/cipher.py) | ✅ |
| **Pág. 7** | *"Processo de cifragem: XOR, Substituição, Permutação, Blocos"* e *"Difusão / Confusão"* | `DynamicSPNCipher` (128b, 8 rodadas CBC: XOR subchave, S-Box, P-Box, `_diffuse_block`) em [apps/api/core/security/cipher.py](apps/api/core/security/cipher.py) | ✅ |
| **Pág. 10** | *"2. Criptografia AES-256 (Cifragem, chaves e integridade)"* | `encrypt_data(..., algorithm="aes-256-gcm")` com `AESGCM` + `SHA-256` em [apps/api/core/security/cipher.py](apps/api/core/security/cipher.py) | ✅ |
| **Pág. 3 / Pág. 10** | *"Implementar esteganografia para ocultação de informações em imagens"* / *"3. Esteganografia"* | `embed_payload_in_png` e `extract_payload_from_png` (LSB PNG + `JTCU` + `SHA-256`) em [apps/api/core/security/steganography.py](apps/api/core/security/steganography.py) | ✅ |
| **Pág. 5** | *"Onde o Big Data será implementado? Coletar logs das operações criptográficas; Registrar tentativas de acesso e falhas de autenticação; Armazenar eventos de detecção de anomalias; Analisar padrões de comportamento; Processar grandes conjuntos de dados experimentais"* | `SecurityEvent` ([apps/api/core/models/security_events.py](apps/api/core/models/security_events.py)), `record_security_event` + `generate_experimental_events` ([apps/api/core/security/anomaly_detector.py](apps/api/core/security/anomaly_detector.py)) e hooks em `LoginView` ([apps/api/core/views.py](apps/api/core/views.py)) | ✅ |
| **Pág. 3 / Pág. 6** | *"Implementar inteligência artificial para detectar comportamentos anormais"* (5 anomalias: auth, descriptografia, arquivos, acesso atípico, geração de eventos) | `detect_anomalies` (`IsolationForest` + `_classify_actor_anomaly`) e `AnomalyAlert` em [apps/api/core/security/anomaly_detector.py](apps/api/core/security/anomaly_detector.py) | ✅ |
| **Pág. 3 / Pág. 8** | *"Simular ataques de força bruta, diferencial e estatístico em ambiente controlado"* | `run_brute_force_attack`, `run_differential_attack`, `run_statistical_attack` em [apps/api/core/security/attacks.py](apps/api/core/security/attacks.py) | ✅ |
| **Pág. 3 / Pág. 9** | *"Avaliar o efeito avalanche, a distribuição estatística e a resistência do sistema"* (4 perguntas da Parte 4) | `evaluate_security_suite` em [apps/api/core/security/attacks.py](apps/api/core/security/attacks.py) | ✅ |
| **Pág. 3 / Pág. 10** | *"Criar um dashboard para visualizar ataques, anomalias e resultados dos testes"* / *"6. Dashboard de segurança"* | Endpoints `/api/security/*` ([apps/api/core/security/views.py](apps/api/core/security/views.py)) e `/seguranca` em [SecurityDashboardPage.vue](frontend/src/pages/SecurityDashboardPage/SecurityDashboardPage.vue) | ✅ |
| **Pág. 11** | *"Relatório e slides: Descrição do algoritmo, Funcionamento, Testes realizados, Resultados, Conclusão"* | [docs/Projeto2_Relatorio_Ciberseguranca.pdf](docs/Projeto2_Relatorio_Ciberseguranca.pdf) | ✅ |

---

## 6. Roteiro Rápido de Apresentação (Ao Vivo em `/seguranca`)

1. **Criptografia Dinâmica:** Clique em **Cifrar** duas vezes seguidas com o mesmo texto/segredo e mostre que o `Fingerprint Chave` e o `Ciphertext` mudam (provando que a chave não é fixa).
2. **Esteganografia + Integridade:** Clique em **Ocultar em PNG**, depois **Extrair & Verificar** (sucesso com `SHA-256` íntegro), e então **Simular Adulteração** (mostrando a rejeição imediata e o registro de `FILE_TAMPERED`).
3. **Ataques & Avalanche:** Clique em **Executar Suite de Ataques** para mostrar Força Bruta (12b vs 128b/256b), Avalanche (~50%), Entropia de Shannon, gráfico de distribuição de bytes e o Veredito Automático.
4. **Big Data & IA:** Clique em **Simular Big Data (2k)** e depois em **Rodar IA Anomalias** para exibir o gráfico de distribuição de eventos e os alertas `HIGH`/`CRITICAL` detectados pelo `IsolationForest`.

---

## 7. Como Executar Localmente

```bash
# 1. Subir Postgres, MinIO, RabbitMQ e API otimizada
docker compose up -d --build postgres minio api
docker compose exec api python manage.py migrate

# 2. Rodar testes unitários e o experimento ponta a ponta
PYTHONPATH=shared/src:apps/api pytest apps/api/core/tests/test_security_projeto2.py -v
python3 scripts/run_projeto2_experiments.py

# 3. Subir Frontend e acessar /seguranca
cd frontend && npm install && npm run dev -- --port 5173
```
