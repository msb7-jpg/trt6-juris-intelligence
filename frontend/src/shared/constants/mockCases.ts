import type { HomeInsightKpis, ProcessCase, QuickFilter } from '@/shared/types/cases'

export const QUICK_FILTERS: QuickFilter[] = [
  { id: 'procedentes', label: 'Somente procedentes' },
  { id: 'recentes', label: 'Ultimos 6 meses' },
  { id: 'recife', label: 'Varas de Recife' },
]

export const MOCK_CASES: ProcessCase[] = [
  {
    numeroProcesso: '0000256-48.2025.5.06.0171',
    tribunal: 'TRT6',
    classeNome: 'Acao Trabalhista - Rito Sumarissimo',
    orgaoJulgadorNome: '1a Vara do Trabalho do Cabo',
    dataAjuizamento: '2025-04-15',
    tempoTramitacaoMeses: 30,
    resumoCausa:
      'Reclamacao para pagamento de salario devido com ajuste da peticao inicial sobre jornada de trabalho.',
    decisaoResumo:
      'Acordo homologado com pagamento de R$ 2.500,00 em parcela unica e custas assumidas pela reclamada.',
    palavrasChave: ['acordo', 'salario', 'jornada', 'despacho'],
    statusProcesso: 'arquivado',
    desfecho: 'sentenca_procedente',
    resultadoReclamante: 'ganhou',
    valorCausa: 31399.7,
    custasValorTotal: 50,
    custasPercentual: 2,
    similaridade: 0.96,
  },
  {
    numeroProcesso: '0003987-21.2024.5.06.0007',
    tribunal: 'TRT6',
    classeNome: 'Acao Trabalhista',
    orgaoJulgadorNome: '3a Turma',
    dataAjuizamento: '2024-09-03',
    tempoTramitacaoMeses: 14,
    resumoCausa:
      'Pedido de horas extras em escala 12x36 sem intervalo minimo legal, com reflexos em verbas rescisorias.',
    decisaoResumo:
      'Reconhecida jornada excedente habitual, com condenacao parcial para pagamento de horas extras e reflexos.',
    palavrasChave: ['horas extras', 'escala 12x36', 'intervalo'],
    statusProcesso: 'em andamento',
    desfecho: 'procedente_parcial',
    resultadoReclamante: 'ganhou_parcial',
    valorCausa: 45800,
    custasValorTotal: 916,
    custasPercentual: 2,
    similaridade: 0.92,
  },
  {
    numeroProcesso: '0001122-10.2023.5.06.0011',
    tribunal: 'TRT6',
    classeNome: 'Acao Trabalhista',
    orgaoJulgadorNome: '2a Vara do Trabalho de Recife',
    dataAjuizamento: '2023-11-27',
    tempoTramitacaoMeses: 19,
    resumoCausa:
      'Reclamante alegou supressao de intervalo intrajornada, com controle de ponto inconsistente.',
    decisaoResumo:
      'Provas documentais e testemunhais confirmaram supressao recorrente de intervalo, com deferimento do pedido.',
    palavrasChave: ['intervalo', 'cartao de ponto', 'testemunha'],
    statusProcesso: 'arquivado',
    desfecho: 'sentenca_procedente',
    resultadoReclamante: 'ganhou',
    valorCausa: 28400,
    custasValorTotal: 568,
    custasPercentual: 2,
    similaridade: 0.89,
  },
  {
    numeroProcesso: '0007765-88.2022.5.06.0021',
    tribunal: 'TRT6',
    classeNome: 'Acao Trabalhista',
    orgaoJulgadorNome: '4a Turma',
    dataAjuizamento: '2022-08-19',
    tempoTramitacaoMeses: 25,
    resumoCausa:
      'Discussao sobre acumulacao de funcoes e pagamento de diferencas salariais em contrato terceirizado.',
    decisaoResumo:
      'Pedido de acumulacao de funcoes indeferido, mas reconhecido adicional por desvio funcional pontual.',
    palavrasChave: ['acumulacao', 'terceirizacao', 'desvio funcional'],
    statusProcesso: 'arquivado',
    desfecho: 'improcedente_parcial',
    resultadoReclamante: 'ganhou_parcial',
    valorCausa: 17500,
    custasValorTotal: 350,
    custasPercentual: 2,
    similaridade: 0.81,
  },
  {
    numeroProcesso: '0004550-03.2025.5.06.0009',
    tribunal: 'TRT6',
    classeNome: 'Acao Trabalhista - Rito Sumarissimo',
    orgaoJulgadorNome: '1a Turma',
    dataAjuizamento: '2025-02-07',
    tempoTramitacaoMeses: 9,
    resumoCausa:
      'Empregado pediu adicional noturno e horas in itinere por transporte fornecido pela empresa.',
    decisaoResumo:
      'Condenacao apenas em adicional noturno, com rejeicao do pedido de horas in itinere por ausencia de prova.',
    palavrasChave: ['adicional noturno', 'horas in itinere', 'prova'],
    statusProcesso: 'em andamento',
    desfecho: 'procedente_parcial',
    resultadoReclamante: 'ganhou_parcial',
    valorCausa: 22900,
    custasValorTotal: 458,
    custasPercentual: 2,
    similaridade: 0.78,
  },
]

export const HOME_INSIGHTS: HomeInsightKpis = {
  probabilidadeExito: 82,
  taxaProcedencia: 76,
  valorMedioCondenacao: 42500,
  tempoMedioMeses: 14,
  riscoRecurso: 65,
  argumentosRelevantes: [
    'Sumula 331, IV, TST',
    'Art. 818 da CLT',
    'Tema 725 da Repercussao Geral',
  ],
}
