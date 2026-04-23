<script setup lang="ts">
import BaseCard from '@/shared/components/ui/BaseCard.vue';
import MetricBadge from '@/shared/components/ui/MetricBadge.vue';
import type { ProcessCase } from '@/shared/types/cases';

defineProps<{ item: ProcessCase }>()
</script>

<template>
  <BaseCard>
    <header class="card-head">
      <div>
        <p class="case-number">{{ item.numeroProcesso }}</p>
        <p class="case-meta">{{ item.tribunal }} - {{ item.orgaoJulgadorNome }}</p>
      </div>
      <MetricBadge :score="item.similaridade" />
    </header>
    <p class="summary">
      <strong>Sintese:</strong>
      {{ item.decisaoResumo }}
    </p>
    <div class="tags">
      <span v-for="tag in item.palavrasChave" :key="`${item.numeroProcesso}-${tag}`">#{{ tag }}</span>
    </div>
  </BaseCard>
</template>

<style scoped>
.card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.case-number {
  margin: 0;
  font-weight: 700;
  color: var(--brand-strong);
}

.case-meta {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.86rem;
}

.summary {
  margin: 0.75rem 0;
  line-height: 1.5;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.tags span {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: var(--bg-soft);
  color: var(--text-body);
  font-size: 0.78rem;
  padding: 0.23rem 0.5rem;
}
</style>
