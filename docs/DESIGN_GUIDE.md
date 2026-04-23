# Guia de Design e UX: JusTRT6

Este documento define as diretrizes de design para a interface do usuário da plataforma de busca vetorial e análise preditiva focada no TRT6 (Pernambuco).

## 1. Visão Geral
A aplicação deve deixar de ser um "buscador de palavras-chave" para se tornar um **assistente de estratégia jurídica**. O foco é a interpretação do dado, não apenas a entrega do documento.

## 2. Princípios de Design
*   **Confiança através da Transparência:** Sempre explicar *por que* um resultado é similar (Score de Similaridade).
*   **Eficiência para o Advogado:** Reduzir o tempo de leitura. O usuário deve entender o desfecho do processo sem abrir o PDF.
*   **Acessibilidade:** Design limpo que possa ser usado tanto por um advogado sênior quanto por um trabalhador buscando entender seus direitos.

## 3. Estrutura de Telas (Wireframe Mindset)

### A. Landing de Busca (The "Google" Moment)
*   **Hero:** Centralizado com uma barra de busca larga.
*   **Placeholder:** "Descreva o caso real (ex: Trabalhei 12h sem intervalo de almoço em Recife...)"
*   **Filtros Rápidos:** Botões para "Somente Procedentes", "Últimos 6 meses", "Varas de Recife".

### B. Página de Resultados (A Inteligência em Tela)
Dividida em duas colunas principais:

#### Coluna de Resultados (60%)
*   **Cards de Processos:**
    *   **Cabeçalho:** Número do processo e Órgão Julgador.
    *   **Similarity Badge:** Badge colorido (Verde > 80%, Amarelo 50-80%) indicando a relevância semântica.
    *   **Decision Snapshot:** Resumo de 2 linhas gerado por IA sobre o desfecho.
    *   **Tags:** `#HorasExtras`, `#JustiçaGratuita`, `#SúmulaXXX`.

#### Coluna de Insights/Dashboard (40%)
*   **Widget "Probabilidade de Êxito":** Gráfico de rosca mostrando % de procedência para o tema no TRT6.
*   **Widget "Impacto Financeiro":** Valor médio e mediano das condenações encontradas.
*   **Widget "Argumentação Relevante":** Lista de Artigos da CLT e Súmulas que mais aparecem nos casos de **sucesso**.
*   **Widget "Tempo de Tramitação":** Média de meses até a sentença.

*   **Tipografia:** Inter ou Montserrat (foco em legibilidade de dados numéricos e textos jurídicos).

## 5. Mobile e Responsividade
*   Priorizar a barra de busca e o "Termômetro de Sucesso" no topo.
*   Cards de resultados expansíveis para economizar espaço vertical.

Para versão desktop vamos utilizar uma barra menu lateral com icones modernos, eis aq uma amostra de como os campos especificos de um processo seria

{
  "numero_processo": "0000256-48.2025.5.06.0171",
  "tribunal": "TRT6",
  "classe_nome": "Ação Trabalhista - Rito Sumaríssimo",
  "orgao_julgador_nome": "1ª Vara do Trabalho do Cabo",
  "data_ajuizamento": "2025-04-15",
  "tempo_tramitacao": 30,
  "resumo_causa": "O reclamante, Leandro Marcionilo de Oliveira, entrou com uma ação trabalhista contra a ECAM Terraplennagem e Pavimentação Ltda. buscando o pagamento do salário devido. A causa envolveu a necessidade de emenda da inicial para detalhar a jornada de trabalho e o valor da causa não se coadunava com os pedidos.",
  "tipo_ato_principal": "sentenca",
  "decisao_resumo": "A juíza homologou um acordo entre as partes, onde a reclamada ECAM Terraplennagem e Pavimentação Ltda. pagará ao reclamante R$ 2.500,00 em parcela única, além de pagar as custas do processo.",
  "palavras_chave_processo": [
    "acordo",
    "salário",
    "jornada",
    "ECAM",
    "despacho"
  ],
  "status_processo": "arquivado",
  "desfecho": "sentenca_procedente",
  "resultado_reclamante": "ganhou",
  "palavras_chave_desfecho": [
    "acordo",
    "pagamento",
    "salário",
    "juízo",
    "homologado"
  ],
  "valor_causa": 31399.7,
  "custas_valor_total": 50.0,
  "custas_percentual": 2.0
}