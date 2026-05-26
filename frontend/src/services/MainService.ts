import { API_ENDPOINTS } from '@/shared/constants/api'
import type {
  BuscaSemanticaPayload,
  BuscaSemanticaResponse,
} from '@/shared/types/api'

import { httpClient } from './httpClient'

export interface ProcessoResumo {
  numero_processo: string
  grau: string
}

export class MainService {
  static async buscaSemantica(
    payload: BuscaSemanticaPayload,
  ): Promise<BuscaSemanticaResponse> {
    const { data } = await httpClient.post<BuscaSemanticaResponse>(
      API_ENDPOINTS.buscaSemantica,
      payload,
    )
    return data
  }

  static async listarProcessosSemAnalise(): Promise<ProcessoResumo[]> {
    const { data } = await httpClient.get<ProcessoResumo[]>(
      API_ENDPOINTS.naoPossuemAnalise,
    )
    return data
  }

  static async listarProcessosSemPdf(): Promise<ProcessoResumo[]> {
    const { data } = await httpClient.get<ProcessoResumo[]>(
      API_ENDPOINTS.naoPossuemPdf,
    )
    return data
  }
}
