# JusTRT6 / SecureAI Lab — Cibersegurança Aplicada a Dados e IA (Partes 1 e 2)

> **Branch:** `feat/ciberseguranca-parte1-e-2`  
> **Disciplina:** Cibersegurança Aplicada a Dados e IA — CESAR School (Prof. Renatta Nigro)  
> **Relatório Técnico Final (PDF):** [docs/Projeto2_Relatorio_Ciberseguranca.pdf](docs/Projeto2_Relatorio_Ciberseguranca.pdf)

Este branch concentra a implementação prática, os experimentos e a documentação de **Cibersegurança (Partes 1 e 2)** sobre a arquitetura otimizada do repositório (`Django/DRF`, `PostgreSQL`, `MinIO` e `Vue 3`).

---

## Documentação e Entregáveis

- **Relatório Final em PDF (Pandoc + Eisvogel):** [docs/Projeto2_Relatorio_Ciberseguranca.pdf](docs/Projeto2_Relatorio_Ciberseguranca.pdf)
- **Fonte Markdown do Relatório:** [docs/projeto2_relatorio_final.md](docs/projeto2_relatorio_final.md)
- **Resultados Experimentais Coletados:** [docs/projeto2_relatorio_resultados.md](docs/projeto2_relatorio_resultados.md)
- **Especificação e Arquitetura (Projeto 2):** [docs/projeto2_requisitos_e_arquitetura.md](docs/projeto2_requisitos_e_arquitetura.md)
- **Otimização Docker + `uv`:** [docs/docker_uv_optimization_plan.md](docs/docker_uv_optimization_plan.md)
- **Base da Parte 1 (SecureAI Lab):** [PLANO_ADEQUACAO_SEGURANCA.md](PLANO_ADEQUACAO_SEGURANCA.md) e [Relatório Projeto - SecureAI Lab - Cibersegurança.md](Relatório%20Projeto%20-%20SecureAI%20Lab%20-%20Cibersegurança.md)

---

## Checklist de Rastreabilidade (`Aula 26 - Projeto 2.pdf` $\rightarrow$ Código)

| Página | Trecho / Requisito do PDF | Onde é cumprido no código | Status |
| :---: | :--- | :--- | :---: |
| **Pág. 3 / Pág. 7** | *"Desenvolver um mecanismo de criptografia simétrica com geração dinâmica de chaves"* / *"Chave secreta: Deve influenciar a cifragem; Não pode ser fixa"* | `derive_dynamic_key` (`PBKDF2-HMAC-SHA256` com `salt` 16B e `nonce` 8B aleatórios por operação) em [apps/api/core/security/cipher.py](apps/api/core/security/cipher.py) | ✅ |
| **Pág. 7** | *"Processo de cifragem: XOR, Substituição, Permutação, Blocos"* e *"Difusão / Confusão"* | `DynamicSPNCipher` (blocos de 128 bits, 8 rodadas em CBC: XOR com subchave HMAC, S-Box bijetiva 256B, P-Box e `_diffuse_block`) em [apps/api/core/security/cipher.py](apps/api/core/security/cipher.py) | ✅ |
| **Pág. 10** | *"2. Criptografia AES-256 (Cifragem, chaves e integridade)"* | `encrypt_data(..., algorithm="aes-256-gcm")` com `AESGCM` + digest `SHA-256` em [apps/api/core/security/cipher.py](apps/api/core/security/cipher.py) | ✅ |
| **Pág. 3 / Pág. 10** | *"Implementar esteganografia para ocultação de informações em imagens"* / *"3. Esteganografia"* | `embed_payload_in_png` e `extract_payload_from_png` (LSB em PNG com cabeçalho `JTCU` + verificação `SHA-256`) em [apps/api/core/security/steganography.py](apps/api/core/security/steganography.py) | ✅ |
| **Pág. 5** | *"Onde o Big Data será implementado? Coletar logs das operações criptográficas; Registrar tentativas de acesso e falhas de autenticação; Armazenar eventos de detecção de anomalias; Analisar padrões de comportamento; Processar grandes conjuntos de dados experimentais"* | Model `SecurityEvent` em [apps/api/core/models/security_events.py](apps/api/core/models/security_events.py), `record_security_event` + `generate_experimental_events` (`bulk_create` + snapshot MinIO) em [apps/api/core/security/anomaly_detector.py](apps/api/core/security/anomaly_detector.py) e hooks em `LoginView` ([apps/api/core/views.py](apps/api/core/views.py)) e [apps/api/core/security/views.py](apps/api/core/security/views.py) | ✅ |
| **Pág. 3 / Pág. 6** | *"Implementar inteligência artificial para detectar comportamentos anormais"* (5 anomalias: tentativas de auth, falhas de descriptografia, alterações em arquivos, acesso atípico, geração de eventos) | `detect_anomalies` (`IsolationForest` via `scikit-learn` + `_classify_actor_anomaly`) e model `AnomalyAlert` em [apps/api/core/security/anomaly_detector.py](apps/api/core/security/anomaly_detector.py) e [apps/api/core/models/security_events.py](apps/api/core/models/security_events.py) | ✅ |
| **Pág. 3 / Pág. 8** | *"Simular ataques de força bruta, diferencial e estatístico em ambiente controlado"* | `run_brute_force_attack`, `run_differential_attack` e `run_statistical_attack` em [apps/api/core/security/attacks.py](apps/api/core/security/attacks.py) | ✅ |
| **Pág. 3 / Pág. 9** | *"Avaliar o efeito avalanche, a distribuição estatística e a resistência do sistema"* (4 perguntas da Parte 4) | `evaluate_security_suite` (avalanche 1-bit texto/chave, entropia de Shannon, $\chi^2$ e `verdict`) em [apps/api/core/security/attacks.py](apps/api/core/security/attacks.py) | ✅ |
| **Pág. 3 / Pág. 10** | *"Criar um dashboard para visualizar ataques, anomalias e resultados dos testes"* / *"6. Dashboard de segurança"* | Endpoints `/api/security/*` ([apps/api/core/security/views.py](apps/api/core/security/views.py), [apps/api/api/urls.py](apps/api/api/urls.py)) e rota `/seguranca` em [frontend/src/pages/SecurityDashboardPage/SecurityDashboardPage.vue](frontend/src/pages/SecurityDashboardPage/SecurityDashboardPage.vue) + [frontend/src/services/security.ts](frontend/src/services/security.ts) | ✅ |
| **Pág. 11** | *"Relatório e slides: Descrição do algoritmo, Funcionamento, Testes realizados, Resultados, Conclusão"* | Relatório compilado com métricas reais e screenshots em [docs/Projeto2_Relatorio_Ciberseguranca.pdf](docs/Projeto2_Relatorio_Ciberseguranca.pdf) | ✅ |

---

## Como Executar

### 1. Subir Backend (`postgres`, `minio`, `rabbitmq`, `api`)
```bash
docker compose up -d --build postgres minio api
docker compose exec api python manage.py migrate
```

### 2. Executar Testes Unitários & Experimento Ponta a Ponta
```bash
# Testes unitários do módulo de segurança
PYTHONPATH=shared/src:apps/api pytest apps/api/core/tests/test_security_projeto2.py -v

# Experimento completo contra a API (gera docs/projeto2_relatorio_resultados.md)
python3 scripts/run_projeto2_experiments.py
```

### 3. Subir Frontend e Acessar o Dashboard
```bash
cd frontend
npm install
npm run dev -- --port 5173
```
Acesse `http://localhost:5173/seguranca` (ou a porta exibida pelo Vite).
