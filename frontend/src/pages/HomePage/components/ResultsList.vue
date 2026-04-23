<script setup lang="ts">
import type { ProcessCase } from '@/shared/types/cases';
import ResultCard from './ResultCard.vue';

defineProps<{ items: ProcessCase[] }>()
</script>

<template>
  <section class="results-list">
    <header>
      <h2>Resultados encontrados ({{ items.length }})</h2>
      <p>Top 5 casos semanticamente proximos para seu contexto.</p>
    </header>
    <div
      v-for="(item, idx) in items"
      :key="item.numeroProcesso"
      v-motion
      :initial="{ opacity: 0, y: 16 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: idx * 70 } }"
    >
      <ResultCard :item="item" />
    </div>
  </section>
</template>

<style scoped>
.results-list {
  display: grid;
  gap: 0.8rem;
}

header {
  margin-bottom: 0.2rem;
}

h2 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
  letter-spacing: -0.02em;
}

p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
}
</style>
