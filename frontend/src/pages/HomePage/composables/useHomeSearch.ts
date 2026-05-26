import { computed, ref } from 'vue'

import { useBuscaSemantica } from '@/composables/useBuscaSemantica'

import { useHomeInsights } from './useHomeInsights'

export function useHomeSearch() {
  const query = ref('')
  const hasSearched = ref(false)
  const submittedQuery = ref('')

  const enabled = computed(
    () => hasSearched.value && submittedQuery.value.trim().length > 0,
  )

  const {
    data: cases,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
  } = useBuscaSemantica(submittedQuery, enabled)

  const insights = useHomeInsights(cases)

  function submitSearch(value: string) {
    const trimmed = value.trim()
    if (!trimmed) return
    query.value = trimmed
    submittedQuery.value = trimmed
    hasSearched.value = true
  }

  return {
    query,
    hasSearched,
    submitSearch,
    cases,
    isLoading,
    isFetching,
    isError,
    error,
    refetch,
    insights,
  }
}
