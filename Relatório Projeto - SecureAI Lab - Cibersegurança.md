

| ![][image1]![][image2] | Projeto:  | SecureAI Lab \- Construção, Ataque e Proteção de uma Aplicação Segura |
| ----: | ----- | :---- |
|  | **Disciplina:**  | Cibersegurança Aplicada a Dados e IA |
|  | **Curso:**  | Ciência da Computação |
|  | **Professora:**  | Renatta Nigro |

**Instruções**: 

● Nesta unidade, vocês deverão desenvolver uma aplicação digital funcional, aplicando princípios de cibersegurança, proteção de dados e segurança de aplicações. 

● O objetivo é projetar e implementar uma aplicação que demonstre: 

confidencialidade, integridade, disponibilidade, autenticação, autorização, proteção de dados, segurança de APIs e segurança no uso de Inteligência Artificial. 

● O projeto deverá integrar desenvolvimento, análise de vulnerabilidades, exploração controlada, correção e validação, demonstrando fundamentação técnica nas decisões tomadas como desenvolvedor. 

● A aplicação deverá ser inicialmente desenvolvida em um ambiente controlado e, posteriormente, submetida a testes de segurança realizados pela própria equipe ou por outra equipe. 

**Objetivo geral:** 

Desenvolver uma aplicação digital funcional que demonstre a aplicação prática de conceitos de cibersegurança, proteção de dados e Inteligência Artificial, realizando um ciclo completo de: Desenvolvimento → Análise → Exploração → Correção → Reteste. 

**O que será desenvolvido?** 

Cada equipe deverá: 

1\. Escolher um problema ou contexto de aplicação.   
2\. Definir o público-alvo e os tipos de usuários do sistema.   
3\. Definir os dados que serão tratados pela aplicação.   
4\. Desenvolver uma aplicação web funcional.   
5\. Implementar autenticação e diferentes níveis de autorização.   
6\. Implementar uma API e banco de dados.   
7\. Implementar mecanismos de proteção de dados.   
8\. Realizar uma análise de ameaças e riscos.   
9\. Identificar e explorar vulnerabilidades de forma controlada.   
10\. Corrigir as vulnerabilidades identificadas.   
11\. Realizar novo teste para verificar a eficácia das correções.   
12\. Analisar os riscos relacionados ao uso de Inteligência Artificial.   
13\. Utilizar IA como ferramenta de apoio à análise de segurança.   
14\. Entregar relatório técnico.   
15\. Apresentar e defender tecnicamente as decisões tomadas.  
**Quais são os requisitos obrigatórios do projeto?** 

A aplicação deverá conter, no mínimo: 

1\. Sistema de autenticação.   
2\. Pelo menos 2 níveis de privilégio, por exemplo: usuário e administrador. 3\. Banco de dados. 

4\. API ou conjunto de endpoints.   
5\. Dados pessoais fictícios.   
6\. Pelo menos uma funcionalidade que envolva manipulação de arquivos ou dados. 7\. Comunicação utilizando HTTPS, quando tecnicamente aplicável. 

8\. Mecanismo de controle de acesso/autorização.   
9\. Pelo menos um mecanismo de proteção criptográfica.   
10\. Utilização de função hash para verificação de integridade ou outra finalidade tecnicamente justificada. 

11\. Uma funcionalidade relacionada à Inteligência Artificial, como chatbot, classificação, análise ou geração de conteúdo. 

12\. Registro de eventos relevantes de segurança (logs). 

A aplicação deverá permitir a demonstração prática dos mecanismos de segurança implementados. 

Não será aceita uma aplicação composta apenas por telas estáticas, CRUD simples ou navegação entre páginas sem funcionalidades reais. 

**Como será a etapa de análise de segurança?** 

Antes dos testes, cada equipe deverá realizar uma análise da própria aplicação. Deverão ser identificados: 

1\. Ativos. 

2\. Dados tratados. 

3\. Usuários e privilégios. 

4\. Superfícies de ataque. 

5\. Ameaças. 

6\. Vulnerabilidades potenciais. 

7\. Impactos. 

8\. Riscos. 

9\. Controles de segurança necessários. 

A equipe deverá produzir uma **Matriz de Riscos**. 

**Como será a etapa de exploração?** 

Cada equipe deverá identificar e demonstrar vulnerabilidades reais ou simuladas em ambiente controlado. 

A exploração deverá apresentar: Vulnerabilidade → Método de exploração → Evidência → Impacto 

**Quais categorias de vulnerabilidades deverão ser investigadas?** A equipe deverá investigar, de acordo com a arquitetura da aplicação:  
1\. Falhas de autenticação. 

2\. Falhas de autorização. 

3\. Controle de acesso inadequado. 

4\. Injeção. 

5\. XSS. 

6\. Exposição indevida de dados. 

7\. Falhas de configuração. 

8\. Problemas de gerenciamento de sessão. 

9\. Falhas em APIs. 

10\. Upload inseguro de arquivos. 

11\. Ausência ou utilização inadequada de criptografia. 

12\. Falhas de integridade. 

13\. Vulnerabilidades relacionadas ao uso de IA. 

A equipe não precisa implementar todas essas vulnerabilidades. 

Deverá identificar quais são relevantes para sua aplicação e justificar tecnicamente sua seleção. 

**Como será a etapa de correção?** 

Após identificar uma vulnerabilidade, a equipe deverá implementar uma correção. Para cada vulnerabilidade, deverá apresentar: 

**Antes da correção** 

● código ou configuração vulnerável; 

● evidência da exploração; 

● impacto. 

**Depois da correção** 

● código ou configuração corrigida; 

● justificativa técnica; 

● mecanismo de proteção utilizado. 

**Reteste** 

O mesmo teste deverá ser realizado novamente para verificar se a vulnerabilidade foi efetivamente mitigada. O objetivo é demonstrar: Ataque funcionando → correção → ataque bloqueado. 

**Como a criptografia deverá ser aplicada?** 

A equipe deverá utilizar os conceitos estudados durante a unidade. Deverá justificar tecnicamente: 

1\. Onde utilizar criptografia simétrica.  
2\. Onde utilizar criptografia assimétrica. 

3\. Onde utilizar funções hash. 

4\. Como proteger senhas. 

5\. Como proteger dados sensíveis. 

6\. Como proteger dados em trânsito. 

7\. Quando utilizar assinatura digital. 

8\. Como ocorre o gerenciamento das chaves. 

Não serão aceitas justificativas como: “Escolhemos porque é mais seguro.” **Como será avaliada a integridade?** 

A equipe deverá demonstrar uma situação em que seja necessário verificar se um dado ou arquivo foi alterado, como por exemplo na utilização de SHA-256. 

**Como será avaliada a segurança da IA?** 

A aplicação deverá possuir pelo menos uma funcionalidade envolvendo IA. 

A equipe deverá analisar os riscos relacionados ao uso dessa tecnologia, além disso, precisam demonstrar pelo menos um cenário de risco relacionado à IA e propor uma mitigação. 

**Como a IA poderá ser utilizada pela equipe?** 

A utilização de Inteligência Artificial durante o desenvolvimento e a análise será permitida e incentivada. A IA poderá ser utilizada para: 

● análise de código; 

● identificação de vulnerabilidades; 

● geração de casos de teste; 

● análise de logs; 

● análise de ameaças; 

● sugestão de controles; 

● documentação; 

● apoio à investigação. 

A resposta produzida pela IA não deverá ser considerada automaticamente correta. A equipe deverá demonstrar como as informações foram testadas, verificadas e validadas. 

Deverá ser registrado: 

1\. Qual ferramenta foi utilizada. 

2\. Para qual finalidade. 

3\. Quais perguntas/prompts foram utilizados. 

4\. Qual foi a resposta obtida. 

5\. O que foi aproveitado. 

6\. O que foi descartado.  
7\. Como a informação foi validada. 

**Como será avaliada a anonimização?**   
Quando houver utilização de dados para testes ou análises, a equipe deverá demonstrar uma técnica de proteção, como: 

● mascaramento;   
● pseudonimização;   
● anonimização. 

**Como será o desafio entre equipes?** 

Após a conclusão da primeira versão da aplicação, cada equipe poderá receber a aplicação de outra equipe para realizar uma avaliação de segurança controlada. A equipe atacante deverá tentar identificar vulnerabilidades e registrar: 

1\. Vulnerabilidade.   
2\. Evidência.   
3\. Método utilizado.   
4\. Impacto.   
5\. Severidade.   
6\. Recomendação. 

A equipe responsável pela aplicação deverá posteriormente analisar os resultados e realizar as correções necessárias. 

**Como será a fundamentação teórica?** 

Todas as decisões deverão ser justificadas com base nos conceitos estudados em sala: 

● Tríade CIA.   
● Gestão de riscos.   
● Ameaças e vulnerabilidades.   
● Criptografia simétrica.   
● Criptografia assimétrica.   
● Funções hash.   
● Integridade.   
● Certificados digitais.   
● SSL/TLS.   
● HTTPS.   
● Autenticação.   
● MFA.   
● Autorização.   
● Zero Trust.   
● Proteção de dados.   
● LGPD.   
● Anonimização.   
● Pseudonimização.   
● Segurança de aplicações.   
● Segurança de IA. 

**Como será a entrega?** 

1\. Aplicação funcional   
Link ou acesso à aplicação.  
2\. Código-fonte   
Repositório contendo o código da aplicação. 

3\. Relatório técnico 

6 a 10 páginas, contendo a análise e evidências de todas as aplicações. 

4\. Evidências dos testes 

Screenshots, logs, resultados dos testes, registros de vulnerabilidades e demonstrações antes/depois. 

5\. Registro de utilização de IA 

Prompts utilizados, respostas relevantes e validação realizada. 

6\. Apresentação oral 

Apresentação na data definida \- 17/09 e 22/09 

**Sugestão da estruturação do relatório:** 

1\. Introdução 

2\. Contextualização da aplicação 

3\. Problema e público-alvo 

4\. Arquitetura da solução 

5\. Ativos e dados tratados 

6\. Threat modeling 

7\. Análise de riscos 

8\. Mecanismos de autenticação e autorização 

9\. Estratégia criptográfica 

10\. Integridade e funções hash 

11\. Segurança da aplicação e APIs 

12\. Segurança da IA 

13\. Proteção de dados e LGPD 

14\. Anonimização/pseudonimização 

15\. Vulnerabilidades identificadas 

16\. Evidências de exploração 

17\. Correções e hardening 

18\. Reteste 

19\. Uso e validação da IA 

20\. Análise crítica 

21\. Considerações finais 

22\. Referências 

**Apresentação oral:** 

Cada equipe terá 15 minutos para apresentação. E deverá ser priorizado demonstrações práticas, e não apenas slides. A equipe deverá demonstrar: 

● A aplicação funcionando.  
● Uma vulnerabilidade sendo explorada. 

● A correção implementada. 

● O mesmo teste sendo realizado novamente. ● Um mecanismo de segurança funcionando. ● A aplicação da IA. 

● Um risco relacionado à IA. 

● As principais decisões técnicas.

| Critério  | Peso |
| ----- | ----- |
| **Desenvolvimento e arquitetura da aplicação** | **10%** |
| **Threat modeling e análise de riscos**  | **10%** |
| **Identificação e exploração de  vulnerabilidades** | **15%** |
| **Criptografia e proteção de dados**  | **10%** |
| **Autenticação, autorização e controle de acesso** | **10%** |
| **Segurança de aplicações e APIs**  | **10%** |
| **Segurança da Inteligência Artificial**  | **10%** |
| **LGPD, anonimização e privacidade**  | **5%** |
| **Hardening e correção das vulnerabilidades**  | **10%** |
| **Reteste e apresentação de evidências**  | **5%** |
| **Uso crítico e responsável de IA**  | **3%** |
| **Documentação e apresentação**  | **2%** |
| **TOTAL**  | **100%** |

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAK8AAABtCAYAAADXsjHKAAAAYUlEQVR4Xu3BgQAAAADDoPlTX+EAVQEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnAYqiAABa3JaFwAAAABJRU5ErkJggg==>