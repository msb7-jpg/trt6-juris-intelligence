import { applyHomeFilters, rankByQuery } from '@/pages/HomePage/utils/searchMatching'
import { HOME_INSIGHTS, MOCK_CASES } from '@/shared/constants/mockCases'
import { computed, ref } from 'vue'

export function useHomeSearch() {
  const query = ref('')
  const hasSearched = ref(false)
  const activeFilters = ref(new Set<string>())

  function toggleFilter(filterId: string) {
    const next = new Set(activeFilters.value)
    if (next.has(filterId)) next.delete(filterId)
    else next.add(filterId)
    activeFilters.value = next
  }

  function submitSearch(value: string) {
    query.value = value
    hasSearched.value = true
  }

  const filteredCases = computed(() => {
    const filtered = applyHomeFilters(MOCK_CASES, activeFilters.value)
    return rankByQuery(filtered, query.value).slice(0, 5)
  })

  return {
    query,
    hasSearched,
    activeFilters,
    filteredCases,
    insightKpis: HOME_INSIGHTS,
    toggleFilter,
    submitSearch,
  }
}
