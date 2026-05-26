export interface ClasseDTO {
  codigo: string
  nome: string
}

export interface OrgaoJulgadorDTO {
  id?: number
  codigo: number
  nome: string
  codigo_municipio_ibge: number | null
}

export interface AssuntoDTO {
  id?: number
  codigo: number
  nome: string
}

export interface PalavraChaveDTO {
  id?: number
  nome: string
}

export type TipoAtoPrincipal =
  | 'acordo_homologado'
  | 'sentenca'
  | 'acordao'
  | 'despacho'
  | 'outro'

export type StatusProcesso =
  | 'arquivado'
  | 'acordo_homologado'
  | 'sentenciado'
  | 'em_andamento'

export type Desfecho =
  | 'acordo_favoravel'
  | 'sentenca_procedente'
  | 'sentenca_parcialmente_procedente'
  | 'sentenca_improcedente'
  | 'extinta'
  | 'arquivado_sem_decisao'
  | 'outro'

export type ResultadoReclamante =
  | 'ganhou'
  | 'ganhou_parcial'
  | 'perdeu'
  | 'sem_decisao'

export interface AnaliseDTO {
  id: number
  resumo: string
  tipo_ato_principal: TipoAtoPrincipal
  decisao: string
  palavras_chave: PalavraChaveDTO[]
  status: StatusProcesso
  desfecho: Desfecho
  resultado_reclamante: ResultadoReclamante
  valor_causa: string
  custas_valor_total: string
}

export interface ProcessoDTO {
  id: number
  numero_processo: string
  classe: ClasseDTO
  tribunal: string
  data_hora_ultima_atualizacao: string
  grau: string
  data_ajuizamento: string
  orgao_julgador: OrgaoJulgadorDTO
  assuntos: AssuntoDTO[]
  analise: AnaliseDTO | null
  similaridade: number
}

export interface BuscaSemanticaPayload {
  consulta: string
  top_k: number
}

export interface BuscaSemanticaResponse {
  items: ProcessoDTO[]
}
