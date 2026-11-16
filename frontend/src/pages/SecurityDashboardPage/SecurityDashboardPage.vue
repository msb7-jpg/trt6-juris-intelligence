<script setup lang="ts">
import {
  securityService,
  type AttackSuiteResponse,
  type CryptoAlgorithm,
  type EncryptedPayload,
  type SecurityDashboardResponse,
  type StegoEmbedResponse,
} from '@/services/security'
import { Activity, AlertTriangle, BrainCircuit, Database, Image as ImageIcon, Lock, ShieldCheck, Swords, Unlock } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const loadingDashboard = ref(false)
const dashboard = ref<SecurityDashboardResponse | null>(null)
const statusMessage = ref('')
const errorMessage = ref('')

// Crypto & Stego Lab state
const plaintext = ref('Dados sigilosos do processo TCU-2026 para cifragem dinamica e esteganografia.')
const secret = ref('ChaveSecretaDinamica#2026')
const algorithm = ref<CryptoAlgorithm>('spn')
const encryptedResult = ref<EncryptedPayload | null>(null)
const decryptedText = ref('')
const stegoResult = ref<StegoEmbedResponse | null>(null)
const stegoFile = ref<File | null>(null)
const extractedText = ref('')

// Attack Simulation state
const runningAttacks = ref(false)
const attackSuite = ref<AttackSuiteResponse | null>(null)

// Big Data + AI state
const runningBigData = ref(false)
const runningAI = ref(false)

async function loadDashboard() {
  loadingDashboard.value = true
  errorMessage.value = ''
  try {
    dashboard.value = await securityService.getDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao carregar dashboard de seguranca.'
  } finally {
    loadingDashboard.value = false
  }
}

async function handleEncrypt() {
  errorMessage.value = ''
  decryptedText.value = ''
  try {
    encryptedResult.value = await securityService.encrypt(plaintext.value, secret.value, algorithm.value)
    statusMessage.value = `Dados cifrados com ${algorithm.value.toUpperCase()} (fingerprint: ${encryptedResult.value.key_fingerprint}).`
    await loadDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Falha ao cifrar.'
  }
}

async function handleDecrypt() {
  if (!encryptedResult.value) return
  errorMessage.value = ''
  try {
    const res = await securityService.decrypt(encryptedResult.value, secret.value)
    decryptedText.value = res.plaintext
    statusMessage.value = 'Dados decifrados e integridade SHA-256 verificada.'
    await loadDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Falha na descriptografia.'
    await loadDashboard()
  }
}

function onStegoFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  stegoFile.value = target.files?.[0] ?? null
}

async function handleStegoEmbed() {
  if (!encryptedResult.value) return
  errorMessage.value = ''
  extractedText.value = ''
  try {
    stegoResult.value = await securityService.embedSteganography(JSON.stringify(encryptedResult.value), stegoFile.value)
    statusMessage.value = `Payload ocultado em imagem PNG (${stegoResult.value.capacity_used_pct}% da capacidade LSB).`
    await loadDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro na esteganografia.'
  }
}

function handleDownloadStegoPng() {
  if (!stegoResult.value) return
  const link = document.createElement('a')
  link.href = `data:image/png;base64,${stegoResult.value.stego_image_b64}`
  link.download = 'stego_payload.png'
  link.click()
}

async function handleStegoExtract(tamper = false) {
  if (!stegoResult.value && !stegoFile.value) return
  errorMessage.value = ''
  try {
    let b64 = stegoResult.value?.stego_image_b64 ?? ''
    if (tamper && b64.length > 40) {
      const mid = Math.floor(b64.length / 2)
      const flippedChar = b64[mid] === 'A' ? 'B' : 'A'
      b64 = b64.slice(0, mid) + flippedChar + b64.slice(mid + 1)
    }
    const res = await securityService.extractSteganography(b64, tamper ? null : stegoFile.value)
    extractedText.value = res.extracted_payload
    statusMessage.value = 'Payload extraido da imagem PNG com hash SHA-256 integro.'
    await loadDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Falha na extracao (integridade violada).'
    await loadDashboard()
  }
}

async function handleRunAttacks() {
  runningAttacks.value = true
  errorMessage.value = ''
  try {
    attackSuite.value = await securityService.runAttackSuite(plaintext.value, secret.value, algorithm.value)
    statusMessage.value = 'Simulacao de ataques (Forca Bruta, Diferencial e Estatistico) concluida.'
    await loadDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao executar ataques.'
  } finally {
    runningAttacks.value = false
  }
}

async function handleSimulateBigData() {
  runningBigData.value = true
  errorMessage.value = ''
  try {
    const res = await securityService.simulateBigData(2000)
    statusMessage.value = `Big Data: ${res.inserted_events} eventos inseridos${res.minio_snapshot ? ` e snapshot salvo em ${res.minio_snapshot}` : ''}.`
    await loadDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro ao simular Big Data.'
  } finally {
    runningBigData.value = false
  }
}

async function handleDetectAnomalies() {
  runningAI.value = true
  errorMessage.value = ''
  try {
    const res = await securityService.detectAnomalies()
    statusMessage.value = `IA IsolationForest analisou ${res.analyzed_actors} atores e detectou ${res.anomalies_detected} anomalias.`
    await loadDashboard()
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Erro na deteccao de anomalias.'
  } finally {
    runningAI.value = false
  }
}

const eventsChartSeries = computed(() => [
  {
    name: 'Eventos',
    data: (dashboard.value?.events_by_type ?? []).map((item) => item.count),
  },
])

const eventsChartOptions = computed(() => ({
  chart: { type: 'bar' as const, toolbar: { show: false } },
  xaxis: {
    categories: (dashboard.value?.events_by_type ?? []).map((item) => item.event_type),
  },
  colors: ['#2563eb'],
  dataLabels: { enabled: false },
}))

const entropyChartSeries = computed(() => [
  {
    name: 'Bytes por Faixa (0-255)',
    data: attackSuite.value?.statistical.byte_bucket_histogram ?? [],
  },
])

const entropyChartOptions = {
  chart: { type: 'bar' as const, toolbar: { show: false } },
  xaxis: {
    categories: Array.from({ length: 16 }, (_, idx) => `${idx * 16}-${idx * 16 + 15}`),
  },
  colors: ['#0f766e'],
  dataLabels: { enabled: false },
}

onMounted(() => {
  void loadDashboard()
})
</script>

<template>
  <section class="security-page">
    <header class="page-header">
      <div>
        <h1><ShieldCheck :size="24" /> Dashboard de Seguranca, Criptografia & IA</h1>
        <p>Projeto 2 — Criptografia Dinamica, Esteganografia LSB, Big Data, Deteccao de Anomalias e Analise de Ataques</p>
      </div>
      <div class="header-actions">
        <button type="button" class="btn secondary" :disabled="runningBigData" @click="handleSimulateBigData">
          <Database :size="16" /> {{ runningBigData ? 'Gerando...' : 'Simular Big Data (2k)' }}
        </button>
        <button type="button" class="btn primary" :disabled="runningAI" @click="handleDetectAnomalies">
          <BrainCircuit :size="16" /> {{ runningAI ? 'Analisando...' : 'Rodar IA Anomalias' }}
        </button>
      </div>
    </header>

    <div v-if="statusMessage" class="banner ok">{{ statusMessage }}</div>
    <div v-if="errorMessage" class="banner err">{{ errorMessage }}</div>

    <!-- KPIs -->
    <div v-if="dashboard" class="kpi-grid">
      <article class="kpi-card">
        <span class="kpi-label">Total de Eventos (Big Data)</span>
        <strong class="kpi-value">{{ dashboard.kpis.total_events }}</strong>
      </article>
      <article class="kpi-card">
        <span class="kpi-label">Taxa de Falhas</span>
        <strong class="kpi-value">{{ dashboard.kpis.failure_rate_pct }}%</strong>
      </article>
      <article class="kpi-card">
        <span class="kpi-label">Falhas Auth / Decifragem</span>
        <strong class="kpi-value">{{ dashboard.kpis.auth_failures }} / {{ dashboard.kpis.decrypt_failures }}</strong>
      </article>
      <article class="kpi-card warn">
        <span class="kpi-label">Anomalias Detectadas (IA)</span>
        <strong class="kpi-value">{{ dashboard.kpis.total_anomalies }}</strong>
      </article>
    </div>

    <!-- Crypto & Steganography Lab -->
    <div class="grid-two">
      <section class="panel">
        <h2><Lock :size="18" /> 1. Criptografia Simetrica Dinamica</h2>
        <div class="field">
          <label>Algoritmo</label>
          <select v-model="algorithm">
            <option value="spn">SPN Customizada (XOR + S-Box + P-Box + Blocos)</option>
            <option value="aes-256-gcm">AES-256-GCM (Arquitetura Parte 5)</option>
          </select>
        </div>
        <div class="field">
          <label>Chave Mestra (derivada dinamicamente via PBKDF2 + Salt + Nonce)</label>
          <input v-model="secret" type="text" />
        </div>
        <div class="field">
          <label>Texto Claro</label>
          <textarea v-model="plaintext" rows="3" />
        </div>
        <div class="btn-row">
          <button type="button" class="btn primary" @click="handleEncrypt">
            <Lock :size="15" /> Cifrar
          </button>
          <button type="button" class="btn secondary" :disabled="!encryptedResult" @click="handleDecrypt">
            <Unlock :size="15" /> Decifrar
          </button>
        </div>

        <div v-if="encryptedResult" class="result-box">
          <p><strong>Fingerprint Chave:</strong> <code>{{ encryptedResult.key_fingerprint }}</code></p>
          <p><strong>Ciphertext (Base64):</strong> <code class="wrap">{{ encryptedResult.ciphertext_b64 }}</code></p>
          <p><strong>SHA-256 Saida:</strong> <code class="wrap">{{ encryptedResult.ciphertext_sha256 }}</code></p>
        </div>
        <div v-if="decryptedText" class="result-box ok">
          <p><strong>Decifrado:</strong> {{ decryptedText }}</p>
        </div>
      </section>

      <section class="panel">
        <h2><ImageIcon :size="18" /> 2. Esteganografia em Imagem (LSB PNG)</h2>
        <p class="muted">Oculta o payload cifrado nos bits menos significativos da imagem com verificacao SHA-256.</p>
        <div class="field">
          <label>Imagem PNG opcional (se vazio, gera capa sintetica)</label>
          <input type="file" accept="image/png" @change="onStegoFileChange" />
        </div>
        <div class="btn-row">
          <button type="button" class="btn primary" :disabled="!encryptedResult" @click="handleStegoEmbed">
            Ocultar em PNG
          </button>
          <button type="button" class="btn secondary" :disabled="!stegoResult && !stegoFile" @click="handleStegoExtract(false)">
            Extrair & Verificar
          </button>
          <button type="button" class="btn secondary" :disabled="!stegoResult" @click="handleDownloadStegoPng">
            Baixar PNG
          </button>
          <button type="button" class="btn secondary" :disabled="!stegoResult" @click="handleStegoExtract(true)">
            Simular Adulteracao
          </button>
        </div>
        <div v-if="stegoResult" class="stego-preview">
          <img :src="`data:image/png;base64,${stegoResult.stego_image_b64}`" alt="Imagem Esteganografada" />
          <div>
            <p><strong>Dimensoes:</strong> {{ stegoResult.image_dimensions.join('x') }} px</p>
            <p><strong>Capacidade usada:</strong> {{ stegoResult.capacity_used_pct }}%</p>
            <p><strong>SHA-256 PNG:</strong> <code class="wrap">{{ stegoResult.stego_sha256 }}</code></p>
          </div>
        </div>
        <div v-if="extractedText" class="result-box ok">
          <p><strong>Payload Extraido:</strong> <code class="wrap">{{ extractedText }}</code></p>
        </div>
      </section>
    </div>

    <!-- Attack Simulation & Avalanche -->
    <section class="panel">
      <div class="panel-head">
        <h2><Swords :size="18" /> 3. Simulador de Ataques & Avaliacao (Partes 3 e 4)</h2>
        <button type="button" class="btn primary" :disabled="runningAttacks" @click="handleRunAttacks">
          {{ runningAttacks ? 'Executando...' : 'Executar Suite de Ataques' }}
        </button>
      </div>

      <div v-if="attackSuite" class="attack-grid">
        <div class="attack-card">
          <h3>Forca Bruta</h3>
          <p>{{ attackSuite.brute_force.summary }}</p>
          <small>Taxa: {{ attackSuite.brute_force.measured_keys_per_sec }} chaves/s | Espaco completo: {{ attackSuite.brute_force.estimated_years_full_keyspace }} anos</small>
        </div>
        <div class="attack-card">
          <h3>Ataque Diferencial (Avalanche)</h3>
          <p>{{ attackSuite.differential.summary }}</p>
          <small>Ideal: 50% | Medido: {{ attackSuite.differential.avalanche_pct }}%</small>
        </div>
        <div class="attack-card">
          <h3>Ataque Estatistico</h3>
          <p>{{ attackSuite.statistical.summary }}</p>
          <small>Entropia: {{ attackSuite.statistical.shannon_entropy }}/8.0 | Qui-Quadrado: {{ attackSuite.statistical.chi_square }}</small>
        </div>
      </div>

      <div v-if="attackSuite" class="verdict-box">
        <strong>Veredito Automatico:</strong> {{ attackSuite.verdict.justification }}
        <div class="chart-wrap">
          <VueApexCharts type="bar" height="220" :options="entropyChartOptions" :series="entropyChartSeries" />
        </div>
      </div>
    </section>

    <!-- Big Data Chart & AI Anomalies -->
    <div v-if="dashboard" class="grid-two">
      <section class="panel">
        <h2><Activity :size="18" /> 4. Distribuicao de Eventos (Big Data)</h2>
        <VueApexCharts type="bar" height="260" :options="eventsChartOptions" :series="eventsChartSeries" />
      </section>

      <section class="panel">
        <h2><AlertTriangle :size="18" /> 5. Alertas de Anomalias Detectadas (IA)</h2>
        <div v-if="dashboard.recent_alerts.length === 0" class="muted">
          Nenhuma anomalia registrada ainda. Clique em "Simular Big Data (2k)" e "Rodar IA Anomalias".
        </div>
        <ul v-else class="alert-list">
          <li v-for="alert in dashboard.recent_alerts" :key="alert.id" class="alert-item">
            <span class="badge" :class="alert.severity.toLowerCase()">{{ alert.severity }}</span>
            <div>
              <strong>{{ alert.anomaly_type }}</strong> — {{ alert.actor_label }}
              <p>{{ alert.summary }}</p>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </section>
</template>

<style scoped>
.security-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}
.page-header h1 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.35rem;
  margin: 0;
}
.page-header p {
  margin: 0.25rem 0 0;
  color: #64748b;
  font-size: 0.9rem;
}
.header-actions, .btn-row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.95rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
}
.btn.primary { background: #2563eb; color: #fff; }
.btn.secondary { background: #e2e8f0; color: #0f172a; }
.btn:disabled { opacity: 0.55; cursor: not-allowed; }
.banner {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}
.banner.ok { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.banner.err { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.9rem;
}
.kpi-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.kpi-card.warn { border-color: #fdba74; background: #fff7ed; }
.kpi-label { font-size: 0.8rem; color: #64748b; }
.kpi-value { font-size: 1.45rem; color: #0f172a; }
.grid-two {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 1rem;
}
.panel {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.panel h2 {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 1.05rem;
  margin: 0;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.field label { font-size: 0.8rem; font-weight: 600; color: #334155; }
.field input, .field select, .field textarea {
  padding: 0.5rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.88rem;
}
.result-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.7rem;
  font-size: 0.82rem;
}
.result-box.ok { background: #f0fdf4; border-color: #bbf7d0; }
.wrap { word-break: break-all; }
.stego-preview {
  display: flex;
  gap: 0.85rem;
  align-items: center;
  flex-wrap: wrap;
}
.stego-preview img {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
}
.attack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.8rem;
}
.attack-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.8rem;
}
.attack-card h3 { margin: 0 0 0.35rem; font-size: 0.95rem; }
.verdict-box {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 0.85rem;
}
.chart-wrap { margin-top: 0.75rem; }
.alert-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 280px;
  overflow-y: auto;
}
.alert-item {
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  padding: 0.55rem;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 0.84rem;
}
.alert-item p { margin: 0.2rem 0 0; color: #475569; }
.badge {
  padding: 0.15rem 0.45rem;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 700;
}
.badge.critical { background: #fee2e2; color: #991b1b; }
.badge.high { background: #ffedd5; color: #9a3412; }
.badge.medium { background: #fef9c3; color: #854d0e; }
.badge.low { background: #e0f2fe; color: #075985; }
.muted { color: #64748b; font-size: 0.85rem; }
</style>
