<script setup lang="ts">
import EmptyPanel from '@/shared/components/ui/EmptyPanel.vue'
import HomeHero from './components/HomeHero.vue'
import InsightsPanel from './components/InsightsPanel.vue'
import ResultsList from './components/ResultsList.vue'
import SearchBar from './components/SearchBar/SearchBar.vue'
import { useHomeSearch } from './composables/useHomeSearch'

const EMPTY_TITLE = 'Faça uma busca para iniciar'
const EMPTY_DESCRIPTION =
  'Descreva o contexto jurídico para gerar precedentes similares e os principais insights preditivos.'
const LOADING_TITLE = 'Analisando a base de processos…'
const LOADING_DESCRIPTION =
  'Estamos buscando os processos mais relevantes para sua consulta. Isso pode levar alguns segundos.'
const ERROR_TITLE = 'Não foi possível concluir a busca'
const NO_RESULTS_TITLE = 'Nenhum processo encontrado'
const NO_RESULTS_DESCRIPTION =
  'Refine a consulta com termos mais específicos do contexto jurídico.'

const {
  query,
  hasSearched,
  submitSearch,
  cases,
  isLoading,
  isFetching,
  isError,
  error,
  insights,
} = useHomeSearch()
</script>

<template>
  <section class="home-page">
    <div v-motion :initial="{ opacity: 0, y: 12 }" :enter="{ opacity: 1, y: 0 }">
      <HomeHero />
      <SearchBar
        v-model="query"
        :loading="isFetching"
        @submit="submitSearch"
      />
    </div>

    <div
      v-if="!hasSearched"
      v-motion
      :initial="{ opacity: 0, y: 12 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 160 } }"
    >
      <EmptyPanel :title="EMPTY_TITLE" :description="EMPTY_DESCRIPTION" />
    </div>

    <div
      v-else-if="isLoading || isFetching"
      v-motion
      :initial="{ opacity: 0, y: 12 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <EmptyPanel :title="LOADING_TITLE" :description="LOADING_DESCRIPTION" />
    </div>

    <div
      v-else-if="isError"
      v-motion
      :initial="{ opacity: 0, y: 12 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <EmptyPanel
        :title="ERROR_TITLE"
        :description="error?.message ?? 'Tente novamente em instantes.'"
      />
    </div>

    <div
      v-else-if="!cases || cases.length === 0"
      v-motion
      :initial="{ opacity: 0, y: 12 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <EmptyPanel :title="NO_RESULTS_TITLE" :description="NO_RESULTS_DESCRIPTION" />
    </div>

    <div
      v-else
      class="results-grid"
      v-motion
      :initial="{ opacity: 0, y: 14 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 120 } }"
    >
      <ResultsList :items="cases" />
      <InsightsPanel :insights="insights" />
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
