# Projeto 2 — Sistema Criptográfico, Esteganografia, Big Data, IA e Análise de Ataques (`jurisTCU`)

**Disciplina:** Cibersegurança Aplicada a Dados e IA (CESAR School — Prof. Renatta Nigro)  
**Referência:** `Aula 26 - Projeto 2.pdf` (2026 | Novembro)  
**Repositório:** `jurisTCU`

---

## 1. Visão Geral e Arquitetura (6 Camadas)

O módulo de segurança do Projeto 2 foi integrado diretamente à arquitetura existente do `jurisTCU` (`api` Django/DRF + `postgres` + `minio` + `frontend` Vue 3), seguindo o pipeline da Parte 5:

1. **Entrada de Dados:** Texto, dados numéricos, mensagens ou arquivos enviados via API/Dashboard.
2. **Criptografia Simétrica (Dinâmica + AES-256-GCM):**
   - **SPN Customizada em Blocos (128 bits, 8 rodadas):** Derivação dinâmica de chave por sessão via `PBKDF2-HMAC-SHA256` + `salt` aleatório de 16 bytes + nonce (nunca fixa), combinando **XOR** com subchave da rodada, **Substituição** (S-Box) e **Permutação** (P-Box) para garantir **Confusão** e **Difusão**.
   - **AES-256-GCM:** Cifragem autenticada de produção com verificação de integridade (tag GCM + digest SHA-256).
3. **Esteganografia em Imagens (LSB):** Ocultação do payload cifrado + cabeçalho de tamanho + hash SHA-256 nos bits menos significativos (LSB) dos canais RGB de imagens PNG sem perdas.
4. **Big Data (Coleta e Processamento Analítico):** Tabela `SecurityEvent` no PostgreSQL (ingestão em lote via `bulk_create`, índices temporais e agregações SQL) com exportação de snapshots analíticos JSON para o **MinIO** (S3), registrando operações criptográficas, tentativas/falhas de autenticação, falhas de descriptografia, checagens de integridade e cargas experimentais (10k–50k+ eventos).
5. **Inteligência Artificial (Detecção de Anomalias):** Pipeline com `IsolationForest` (`scikit-learn`) e fallback estatístico Z-Score analisando janelas comportamentais para identificar:
   - Número incomum de tentativas de autenticação (`AUTH_BRUTE_FORCE`);
   - Frequência elevada de falhas de descriptografia (`HIGH_DECRYPT_FAIL_RATE`);
   - Alterações inesperadas em arquivos / hash mismatch (`FILE_ALTERATION`);
   - Padrões atípicos de acesso (`ATYPICAL_ACCESS_PATTERN`);
   - Comportamentos incomuns na geração de eventos (`EVENT_BURST`).
6. **Dashboard de Segurança (`/seguranca`):** Interface interativa em Vue 3 (`vue3-apexcharts`) para operar o pipeline cifragem $\rightarrow$ esteganografia $\rightarrow$ extração, executar os 3 ataques controlados, simular carga Big Data, disparar a IA de anomalias e visualizar gráficos, alertas e vereditos.

---

## 2. Simulação de Ataques e Avaliação (Partes 3 e 4)

| Ataque | O que é avaliado | Métrica / Saída |
| :--- | :--- | :--- |
| **Força Bruta** | Busca exaustiva em espaço reduzido controlado (12–16 bits) + projeção analítica para 128/256 bits | Chaves testadas/s, tempo decorrido, tempo estimado para espaço completo e viabilidade |
| **Ataque Diferencial** | Alteração de 1 bit no texto claro (ou chave) mantendo o restante idêntico | Distância de Hamming e **Efeito Avalanche (%)** — ideal $\approx 50\%$ |
| **Ataque Estatístico** | Distribuição de frequência de bytes do texto cifrado | **Entropia de Shannon** (ideal $\approx 8.0$ bits/byte), teste $\chi^2$ de uniformidade e detecção de padrões |

O sistema gera automaticamente o veredito técnico respondendo às 4 questões da Parte 4:
1. O sistema apresenta efeito avalanche?
2. Existem padrões na saída?
3. Qual ataque foi mais eficaz?
4. O sistema é seguro? Justificativa técnica.

---

## 3. Mapeamento de Arquivos e Endpoints

- **Backend (`apps/api/core/`):**
  - `security/cipher.py`: `DynamicSPNCipher`, `AES256GCMCipher`, derivação dinâmica de chaves.
  - `security/steganography.py`: `embed_payload_in_png`, `extract_payload_from_png`.
  - `security/attacks.py`: `run_brute_force_attack`, `run_differential_attack`, `run_statistical_attack`.
  - `security/anomaly_detector.py`: `generate_experimental_events`, `detect_anomalies`, snapshot no MinIO.
  - `models/security_events.py`: `SecurityEvent`, `AnomalyAlert`, `AttackExperiment`.
  - Endpoints sob `/api/security/`: `encrypt/`, `decrypt/`, `steganography/embed/`, `steganography/extract/`, `attacks/run/`, `bigdata/simulate/`, `ai/detect-anomalies/`, `dashboard/`.
- **Frontend (`frontend/src/`):**
  - `services/security.ts` e `pages/SecurityDashboardPage/SecurityDashboardPage.vue` (rota `/seguranca`).

---

## 4. Roteiro para Relatório e Slides (Parte 5 — até 5,0 pts)

1. **Descrição do algoritmo:** Derivação dinâmica de chaves (`PBKDF2-HMAC-SHA256`), rodadas SPN (XOR, S-Box, P-Box), comparação com AES-256-GCM e esteganografia LSB.
2. **Funcionamento:** Fluxo completo das 6 camadas no `jurisTCU` (API + Postgres + MinIO + IA + Dashboard).
3. **Testes realizados:** Execução dos ataques (Força Bruta, Diferencial/Avalanche, Estatístico) e simulação de massa Big Data + detecção por `IsolationForest`.
4. **Resultados:** Métricas coletadas diretamente do `/api/security/dashboard/` e screenshots dos gráficos.
5. **Conclusão:** Análise crítica da segurança, eficácia dos ataques e papel da IA na detecção de anomalias.
