# Plano de Ação e Adequação — Projeto SecureAI Lab (Cibersegurança)

**Projeto:** JusTRT6 / SecureAI Lab — Construção, Ataque e Proteção de uma Aplicação Segura  
**Disciplina:** Cibersegurança Aplicada a Dados e IA  
**Data:** 15 de Setembro de 2026  

---

> [!IMPORTANT]
> **Diretriz de Execução e Autoatualização Contínua do Plano:**  
> Sempre que qualquer item, funcionalidade, correção ou teste deste plano for implementado no projeto, este arquivo ([PLANO_ADEQUACAO_SEGURANCA.md](file:///home/miguel/workspace/jurisTCU/PLANO_ADEQUACAO_SEGURANCA.md)) **DEVE SER OBRIGATORIAMENTE AUTOATUALIZADO**.  
> A atualização deve:
> 1. Atualizar o status do item na tabela de diagnóstico (de ⚠️/❌ para ✅ Implementado).
> 2. Marcar os passos concluídos na seção correspondente.
> 3. Adicionar uma entrada na seção **8. Registro de Execuções e Atualizações (Log de Mudanças)** descrevendo exatamente o que foi implementado, quais arquivos foram modificados/criados e como testar/validar.

---

## 1. Diagnóstico: Requisitos Obrigatórios vs. Estado Atual do Projeto

| Requisito do Edital / Relatório | Status Atual | O que está faltando |
| :--- | :---: | :--- |
| **1. Autenticação** | ✅ Implementado | Possui Token Auth e endpoints `/auth/register/`, `/auth/login/`, `/auth/logout/`, `/auth/me/`. |
| **2. Pelo menos 2 níveis de privilégio (ex: usuário e admin)** | ⚠️ Incompleto | Apenas `IsAuthenticated` genérico. Não há diferenciação de papéis (RBAC) com permissões distintas nem endpoints restritos a administradores. |
| **3. Banco de dados & API** | ✅ Implementado | PostgreSQL com `pgvector` e endpoints DRF de processos, busca semântica e buscas salvas. |
| **4. Manipulação de arquivos ou dados** | ✅ Implementado | Download de PDFs de processos, armazenamento no MinIO (S3) e extração de texto. |
| **5. Dados pessoais fictícios (LGPD)** | ⚠️ Ausente | Os dados de processos contêm nomes reais/completos de partes e advogados do TRT-6. Falta rotina de anonimização/pseudonimização/mascaramento de dados sensíveis (LGPD). |
| **6. Criptografia Simétrica e Assimétrica** | ⚠️ Parcial | Há hashing de senhas pelo Django, mas falta criptografia de dados em repouso (ex: campos sensíveis com Fernet/AES-256) e justificativa/uso prático de assimétrica (ex: assinatura digital/chaves RSA para validação ou tokens assinados). |
| **7. Função Hash para Integridade (ex: SHA-256)** | ⚠️ Ausente | PDFs e dados extraídos não possuem verificação de integridade via SHA-256 para comprovar se um documento ou dado foi adulterado. |
| **8. Registro de eventos relevantes de segurança (Audit Logs)** | ⚠️ Incompleto | Há logs operacionais via loguru/standard logger, mas não há trilha de auditoria estruturada de eventos de segurança (falhas de login, acessos negados, modificações de privilégio, etc.). |
| **9. Funcionalidade de IA & Análise de Riscos de IA** | ⚠️ Parcial | A IA extrai o resumo e dados jurídicos, mas não há salvaguarda contra **Prompt Injection** / **Jailbreak** via conteúdo malicioso de PDFs ou consultas, nem sanitização/validação dos inputs da LLM. |
| **10. Ciclo de Ataque / Exploração → Correção → Reteste** | ⚠️ Ausente | Faltam os cenários práticos documentados e testáveis para apresentação (ex: BOLA/IDOR, Prompt Injection, Adulteração de Hash). |
| **11. Relatório Técnico e Registro de uso de IA** | ⚠️ A Fazer | Preenchimento das 22 seções obrigatórias do relatório (6 a 10 páginas) e tabela de registro de prompts/validação. |

---

## 2. Detalhamento Técnico das Fases de Implementação

### Fase 1: Controle de Acesso Baseado em Papéis (RBAC)
* **Objetivo:** Cumprir o requisito de pelo menos 2 níveis de privilégio (ex: `ADMIN` e `USER` / `ADVOGADO`).
* **Arquivos afetados:**
  - `apps/api/core/permissions.py` (novo)
  - `apps/api/core/views.py`
  - `apps/api/api/urls.py`
* **Passos de Código:**
  1. Criar classe de permissão DRF `IsAdminRole(BasePermission)` verificando se `request.user.is_staff` ou papel atribuído.
  2. Criar endpoint administrativo protegido (ex: `GET /api/admin/audit-logs/` ou `POST /api/admin/reindexar/`).
  3. Garantir retorno `403 Forbidden` quando um usuário padrão tentar acessar o recurso restrito.

---

### Fase 2: Verificação de Integridade com Funções Hash (SHA-256)
* **Objetivo:** Comprovar a integridade de arquivos/documentos jurídicos e detectar adulteração física ou lógica.
* **Arquivos afetados:**
  - `apps/api/core/models/processo.py`
  - `apps/api/core/services.py`
  - `apps/api/core/views.py`
  - `apps/worker-llm/worker.py`
* **Passos de Código:**
  1. Adicionar campo `pdf_sha256 = models.CharField(max_length=64, blank=True, null=True)` no modelo `Processo`.
  2. No momento em que o PDF é recebido e salvo no S3/MinIO, calcular o hash digest `hashlib.sha256(content).hexdigest()` e persistir no banco.
  3. Criar endpoint de checagem: `GET /api/processos/{id}/verificar-integridade/`:
     - Baixa os bytes atuais do S3, calcula o SHA-256 em tempo real e compara com o valor registrado no banco.
     - Retorna status `INTEGRO` ou `ADULTERADO` (com disparo imediato de alerta de segurança em log).

---

### Fase 3: Proteção de Dados, LGPD & Anonimização / Mascaramento
* **Objetivo:** Cumprir os 5% da avaliação de LGPD e uso de técnicas de proteção (mascaramento/pseudonimização) e criptografia simétrica.
* **Arquivos afetados:**
  - `apps/api/core/security/anonymizer.py` (novo)
  - `apps/api/core/serializers/processo_serializer.py`
  - `shared/encryption.py` (novo)
* **Passos de Código:**
  1. **Mascaramento:** Criar utilitário que substitui dados pessoais identificáveis (nomes de pessoas físicas e CPFs) por versões mascaradas (ex: `123.***.***-00` e `J*** S***`) na camada de serialização pública.
  2. **Criptografia Simétrica (AES-256 via Fernet):** Criar utilitário para cifrar dados sensíveis em repouso (ex: anotações internas ou metadados sigilosos de processos) usando chave secreta proveniente de variável de ambiente (`ENCRYPTION_KEY`).

---

### Fase 4: Segurança da Inteligência Artificial (Mitigação de Prompt Injection)
* **Objetivo:** Atender os 10% de Segurança de IA, demonstrando cenário de ataque de IA (Prompt Injection indireto via documento PDF) e sua mitigação.
* **Arquivos afetados:**
  - `apps/worker-llm/main.py`
  - `shared/llm_constants.py`
* **Passos de Código:**
  1. **Isolamento com Delimitadores Estritos:** Envolver o texto do documento em tags XML/Markdown estritas como `<documento_tribunal_nao_confiavel> ... </documento_tribunal_nao_confiavel>`.
  2. **Filtro de Injeção de Prompts:** Criar validador pré-inferência que analisa padrões maliciosos (ex: `"ignore previous instructions"`, `"system override"`, `"esqueça as regras anteriores"`, etc.).
  3. **Validação de Saída Estruturada:** Garantir que tentativas de manipular campos críticos (como inverter decisões ou injetar scripts na fundamentação) sejam barradas e registradas na auditoria.

---

### Fase 5: Trilha de Auditoria e Logs de Segurança (Security Audit Logs)
* **Objetivo:** Registro obrigatório de eventos relevantes de segurança para auditoria e resposta a incidentes.
* **Arquivos afetados:**
  - `apps/api/core/models/audit_log.py` (novo)
  - `apps/api/core/views.py`
* **Passos de Código:**
  1. Criar model `SecurityAuditLog`:
     - `timestamp`: data/hora do evento
     - `user`: usuário associado (ou None se anônimo)
     - `ip_address`: endereço IP de origem
     - `event_type`: tipo (`LOGIN_FAILED`, `ACCESS_DENIED`, `INTEGRITY_VIOLATION`, `PROMPT_INJECTION_DETECTED`, `DATA_EXPORT`)
     - `severity`: severidade (`INFO`, `WARNING`, `CRITICAL`)
     - `metadata`: detalhes do evento em JSON
  2. Integrar a gravação de logs aos endpoints críticos (falhas de login, acessos 403, violações de integridade de hash).

---

### Fase 6: Cenários de Exploração, Correção e Reteste (15% Exploração + 10% Hardening + 5% Reteste)
Para a demonstração prática e relatório, os 3 cenários selecionados são:

1. **Cenário 1 — Falha de Controle de Acesso / BOLA (Broken Object Level Authorization):**
   - *Exploração:* Usuário sem privilégio tentando acessar/alterar recursos de outro usuário ou endpoint administrativo.
   - *Correção:* Filtros obrigatórios baseados em `request.user` e permissions de papéis.
   - *Reteste:* Demonstração com `curl` retornando `403 Forbidden`.

2. **Cenário 2 — Quebra de Integridade de Arquivo Judicial:**
   - *Exploração:* Adulteração de 1 byte no PDF do processo no storage.
   - *Correção:* Checagem criptográfica por SHA-256 no backend.
   - *Reteste:* Alerta de integridade disparado e acesso bloqueado ao documento corrompido.

3. **Cenário 3 — Ataque de Prompt Injection Indireto em IA:**
   - *Exploração:* PDF judicial contendo instrução oculta para falsificar o resultado da decisão para "GANHOU".
   - *Correção:* Sanitizador de input, delimitadores estritos e validação de schema pós-inferência.
   - *Reteste:* Tentativa de injeção neutralizada com registro no log de segurança.

---

### Fase 7: Estrutura do Relatório Técnico (22 Seções)
Estruturação do documento de 6 a 10 páginas conforme o edital:
1. Introdução
2. Contextualização da aplicação
3. Problema e público-alvo
4. Arquitetura da solução
5. Ativos e dados tratados
6. Threat modeling (STRIDE / DREAD)
7. Análise de riscos (Matriz de Riscos)
8. Mecanismos de autenticação e autorização
9. Estratégia criptográfica
10. Integridade e funções hash
11. Segurança da aplicação e APIs
12. Segurança da IA
13. Proteção de dados e LGPD
14. Anonimização/pseudonimização
15. Vulnerabilidades identificadas
16. Evidências de exploração
17. Correções e hardening
18. Reteste
19. Uso e validação da IA (Tabela de Prompts)
20. Análise crítica
21. Considerações finais
22. Referências

---

## 8. Registro de Execuções e Atualizações (Log de Mudanças)

> *Este registro deve ser atualizado pelo assistente a cada nova implementação, correção ou teste concluído.*

| Data | Fase / Item | O que foi feito | Arquivos Alterados/Criados | Como Validar / Testar |
| :--- | :--- | :--- | :--- | :--- |
| *15/09/2026* | *Inicialização* | *Criação do plano inicial e definição das diretrizes de autoatualização.* | `PLANO_ADEQUACAO_SEGURANCA.md` | Leitura do documento |
