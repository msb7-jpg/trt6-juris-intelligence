<script setup lang="ts">
import BaseCard from '@/shared/components/ui/BaseCard.vue';
import type { HomeInsightKpis } from '@/shared/types/cases';
import { formatCurrencyBRL, formatMonthCount } from '@/shared/utils/formatters';
import { BarChart3, CircleDollarSign, Clock3, Scale, TrendingUp } from 'lucide-vue-next';

defineProps<{ kpis: HomeInsightKpis }>()
</script>

<template>
  <section class="insights-panel">
    <h2>Painel de insights</h2>
    <BaseCard>
      <p class="metric-title"><TrendingUp :size="16" /> Probabilidade de exito</p>
      <div class="metric-value">{{ kpis.probabilidadeExito }}%</div>
      <p class="metric-note">Taxa historica para argumentos semelhantes no TRT6.</p>
    </BaseCard>

    <BaseCard>
      <p class="metric-title"><CircleDollarSign :size="16" /> Valor medio</p>
      <div class="metric-value">{{ formatCurrencyBRL(kpis.valorMedioCondenacao) }}</div>
      <p class="metric-note">Media estimada de acordo ou condenacao em casos correlatos.</p>
    </BaseCard>

    <div class="inline-grid">
      <BaseCard>
        <p class="metric-title"><Clock3 :size="16" /> Tempo medio</p>
        <div class="metric-value small">{{ formatMonthCount(kpis.tempoMedioMeses) }}</div>
      </BaseCard>
      <BaseCard>
        <p class="metric-title"><Scale :size="16" /> Risco de recurso</p>
        <div class="metric-value small">{{ kpis.riscoRecurso }}%</div>
      </BaseCard>
    </div>

    <BaseCard>
      <p class="metric-title"><BarChart3 :size="16" /> Argumentacao relevante</p>
      <ul>
        <li v-for="argumento in kpis.argumentosRelevantes" :key="argumento">{{ argumento }}</li>
      </ul>
    </BaseCard>
  </section>
</template>

<style scoped>
.insights-panel {
  display: grid;
  gap: 0.75rem;
}

h2 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
  letter-spacing: -0.02em;
}

.metric-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  font-weight: 700;
}

.metric-value {
  margin: 0.35rem 0 0;
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--brand-strong);
}

.metric-value.small {
  font-size: 1.25rem;
}

.metric-note {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
}

.inline-grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

ul {
  margin: 0.55rem 0 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.35rem;
}

@media (max-width: 900px) {
  .inline-grid {
    grid-template-columns: 1fr;
  }
}
</style>
