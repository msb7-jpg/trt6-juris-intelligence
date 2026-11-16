import { httpClient } from './httpClient'

export type CryptoAlgorithm = 'spn' | 'aes-256-gcm'

export interface EncryptedPayload {
  algorithm: CryptoAlgorithm
  rounds: number | null
  ciphertext_b64: string
  salt_b64: string
  nonce_b64: string
  iv_b64: string
  plaintext_sha256: string
  ciphertext_sha256: string
  key_fingerprint: string
}

export interface StegoEmbedResponse {
  stego_image_b64: string
  stego_sha256: string
  payload_sha256: string
  payload_size_bytes: number
  capacity_used_pct: number
  image_dimensions: [number, number]
}

export interface StegoExtractResponse {
  extracted_payload: string
  payload_sha256: string
  payload_size_bytes: number
  integrity_verified: boolean
}

export interface AttackSuiteResponse {
  brute_force: {
    reduced_key_bits: number
    reduced_keyspace: number
    attempts_to_crack_reduced: number
    cracked_reduced_key: boolean
    measured_keys_per_sec: number
    full_key_bits: number
    estimated_years_full_keyspace: string
    viable_against_full_key: boolean
    summary: string
  }
  differential: {
    plaintext_avalanche_pct: number
    key_avalanche_pct: number
    avalanche_pct: number
    ideal_avalanche_pct: number
    has_avalanche_effect: boolean
    summary: string
  }
  statistical: {
    sample_size_bytes: number
    unique_bytes: number
    shannon_entropy: number
    max_entropy: number
    chi_square: number
    patterns_detected: boolean
    byte_bucket_histogram: number[]
    summary: string
  }
  verdict: {
    has_avalanche_effect: boolean
    patterns_in_output: boolean
    most_effective_attack: string
    is_system_secure: boolean
    justification: string
  }
}

export interface AnomalyAlertItem {
  id: number
  anomaly_type: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  actor_label: string
  score: number
  event_count: number
  summary: string
  details: Record<string, unknown>
  detected_at: string
}

export interface SecurityDashboardResponse {
  kpis: {
    total_events: number
    failed_events: number
    failure_rate_pct: number
    auth_failures: number
    decrypt_failures: number
    tampered_files: number
    total_anomalies: number
  }
  events_by_type: Array<{ event_type: string; count: number }>
  timeline: Array<{ hour: string; total: number; failures: number }>
  recent_alerts: AnomalyAlertItem[]
  recent_attacks: Array<{
    id: number
    attack_type: string
    algorithm: string
    verdict_summary: string
    created_at: string
  }>
}

export const securityService = {
  async getDashboard(): Promise<SecurityDashboardResponse> {
    const { data } = await httpClient.get<SecurityDashboardResponse>('/security/dashboard/')
    return data
  },

  async encrypt(plaintext: string, secret: string, algorithm: CryptoAlgorithm): Promise<EncryptedPayload> {
    const { data } = await httpClient.post<EncryptedPayload>('/security/encrypt/', {
      plaintext,
      secret,
      algorithm,
    })
    return data
  },

  async decrypt(payload: EncryptedPayload, secret: string): Promise<{ plaintext: string; integrity_verified: boolean }> {
    const { data } = await httpClient.post<{ plaintext: string; integrity_verified: boolean }>('/security/decrypt/', {
      payload,
      secret,
    })
    return data
  },

  async embedSteganography(payload: string, imageFile?: File | null): Promise<StegoEmbedResponse> {
    if (imageFile) {
      const form = new FormData()
      form.append('payload', payload)
      form.append('image', imageFile)
      const { data } = await httpClient.post<StegoEmbedResponse>('/security/steganography/embed/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    }
    const { data } = await httpClient.post<StegoEmbedResponse>('/security/steganography/embed/', {
      payload,
    })
    return data
  },

  async extractSteganography(stegoImageB64: string, imageFile?: File | null): Promise<StegoExtractResponse> {
    if (imageFile) {
      const form = new FormData()
      form.append('image', imageFile)
      const { data } = await httpClient.post<StegoExtractResponse>('/security/steganography/extract/', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    }
    const { data } = await httpClient.post<StegoExtractResponse>('/security/steganography/extract/', {
      stego_image_b64: stegoImageB64,
    })
    return data
  },

  async runAttackSuite(plaintext: string, secret: string, algorithm: CryptoAlgorithm): Promise<AttackSuiteResponse> {
    const { data } = await httpClient.post<AttackSuiteResponse>('/security/attacks/run/', {
      attack_type: 'suite',
      plaintext,
      secret,
      algorithm,
    })
    return data
  },

  async simulateBigData(totalEvents = 2000): Promise<{ inserted_events: number; minio_snapshot: string | null }> {
    const { data } = await httpClient.post<{ inserted_events: number; minio_snapshot: string | null }>(
      '/security/bigdata/simulate/',
      { total_events: totalEvents, inject_anomalies: true, archive_to_minio: true },
    )
    return data
  },

  async detectAnomalies(): Promise<{ analyzed_actors: number; anomalies_detected: number; alerts: AnomalyAlertItem[] }> {
    const { data } = await httpClient.post<{
      analyzed_actors: number
      anomalies_detected: number
      alerts: AnomalyAlertItem[]
    }>('/security/ai/detect-anomalies/')
    return data
  },
}
