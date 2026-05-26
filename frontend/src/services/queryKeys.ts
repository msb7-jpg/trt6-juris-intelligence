import { QUERY_KEYS } from '@/shared/constants/api'

export const queryKeys = {
  buscaSemantica: (consulta: string, topK: number) =>
    [QUERY_KEYS.buscaSemantica, { consulta, topK }] as const,
  naoPossuemAnalise: () => [QUERY_KEYS.naoPossuemAnalise] as const,
  naoPossuemPdf: () => [QUERY_KEYS.naoPossuemPdf] as const,
}
