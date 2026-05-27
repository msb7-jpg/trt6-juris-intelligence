import axios, { AxiosError, type AxiosInstance } from 'axios'

import { ERROR_MESSAGES, HTTP_TIMEOUT_MS } from '@/shared/constants/api'

function resolveBaseURL(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api"
  if (!fromEnv) {
    throw new Error('VITE_API_BASE_URL não está definida. Verifique o arquivo .env.')
  }
  return fromEnv
}

export class HttpError extends Error {
  readonly status: number | null
  readonly cause?: unknown

  constructor(message: string, status: number | null, cause?: unknown) {
    super(message)
    this.name = 'HttpError'
    this.status = status
    this.cause = cause
  }
}

function normalizeError(error: unknown): HttpError {
  if (error instanceof AxiosError) {
    if (error.code === 'ECONNABORTED') {
      return new HttpError(ERROR_MESSAGES.timeout, null, error)
    }
    if (!error.response) {
      return new HttpError(ERROR_MESSAGES.network, null, error)
    }
    const status = error.response.status
    const detail = (error.response.data as { detail?: string } | undefined)?.detail
    return new HttpError(detail ?? ERROR_MESSAGES.unknown, status, error)
  }
  return new HttpError(ERROR_MESSAGES.unknown, null, error)
}

export const httpClient: AxiosInstance = axios.create({
  baseURL: resolveBaseURL(),
  timeout: HTTP_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

httpClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => Promise.reject(normalizeError(error)),
)
