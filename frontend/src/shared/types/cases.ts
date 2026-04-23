export interface ProcessCase {
  numeroProcesso: string
  tribunal: string
  classeNome: string
  orgaoJulgadorNome: string
  dataAjuizamento: string
  tempoTramitacaoMeses: number
  resumoCausa: string
  decisaoResumo: string
  palavrasChave: string[]
  statusProcesso: string
  desfecho: string
  resultadoReclamante: string
  valorCausa: number
  custasValorTotal: number
  custasPercentual: number
  similaridade: number
}

export interface HomeInsightKpis {
  probabilidadeExito: number
  taxaProcedencia: number
  valorMedioCondenacao: number
  tempoMedioMeses: number
  riscoRecurso: number
  argumentosRelevantes: string[]
}

export interface QuickFilter {
  id: string
  label: string
}
