<script setup lang="ts">
import EmptyPanel from '@/shared/components/ui/EmptyPanel.vue'
import HomeHero from './components/HomeHero.vue'
import InsightsPanel from './components/InsightsPanel.vue'
import QuickFilters from './components/QuickFilters.vue'
import ResultsList from './components/ResultsList.vue'
import SearchBar from './components/SearchBar/SearchBar.vue'
import { useHomeSearch } from './composables/useHomeSearch'

const {
  query,
  hasSearched,
  activeFilters,
  filteredCases,
  insightKpis,
  toggleFilter,
  submitSearch,
} = useHomeSearch()
</script>

<template>
  <section class="home-page">
    <div v-motion :initial="{ opacity: 0, y: 12 }" :enter="{ opacity: 1, y: 0 }">
      <HomeHero />
      <SearchBar v-model="query" @submit="submitSearch" />
      <QuickFilters :active-ids="activeFilters" @toggle="toggleFilter" />
    </div>

    <div
      v-if="hasSearched"
      class="results-grid"
      v-motion
      :initial="{ opacity: 0, y: 14 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 120 } }"
    >
      <ResultsList :items="filteredCases" />
      <InsightsPanel :kpis="insightKpis" />
    </div>

    <div
      v-else
      v-motion
      :initial="{ opacity: 0, y: 12 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 160 } }"
    >
      <EmptyPanel
        title="Faça uma busca para iniciar"
        description="Descreva o contexto juridico para gerar 5 precedentes similares e os principais insights preditivos."
      />
    </div>
  </section>
</template>

<style scoped>
.home-page {
  display: grid;
  gap: 1.2rem;
}

.results-grid {
  display: grid;
  gap: 0.9rem;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  align-items: start;
}

@media (max-width: 980px) {
  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
