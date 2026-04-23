import type { ProcessCase } from '@/shared/types/cases'

export function applyHomeFilters(cases: ProcessCase[], activeFilters: Set<string>): ProcessCase[] {
  return cases.filter((item) => {
    if (activeFilters.has('procedentes') && !item.desfecho.includes('procedente')) return false
    if (activeFilters.has('recentes')) {
      const ajuizamentoYear = new Date(item.dataAjuizamento).getFullYear()
      if (ajuizamentoYear < 2024) return false
    }
    if (activeFilters.has('recife') && !item.orgaoJulgadorNome.toLowerCase().includes('recife')) {
      return false
    }
    return true
  })
}

export function rankByQuery(cases: ProcessCase[], query: string): ProcessCase[] {
  const normalized = query.trim().toLowerCase()
  if (!normalized) return cases.slice().sort((a, b) => b.similaridade - a.similaridade)

  return cases
    .map((item) => {
      const corpus = `${item.resumoCausa} ${item.decisaoResumo} ${item.palavrasChave.join(' ')}`.toLowerCase()
      const keywordHits = normalized
        .split(' ')
        .filter((token) => token.length > 2)
        .reduce((acc, token) => (corpus.includes(token) ? acc + 1 : acc), 0)
      const weighted = item.similaridade + keywordHits * 0.01
      return { ...item, similaridade: Number(Math.min(weighted, 0.99).toFixed(2)) }
    })
    .sort((a, b) => b.similaridade - a.similaridade)
}
