<script setup lang="ts">
import BaseCard from '@/shared/components/ui/BaseCard.vue'
import EmptyPanel from '@/shared/components/ui/EmptyPanel.vue'
import { Clock3, ExternalLink, Trash2 } from 'lucide-vue-next'
import { ref } from 'vue'

interface SavedSearch {
  id: string
  title: string
  updatedAt: string
  query: string
}

const savedSearches = ref<SavedSearch[]>([
  {
    id: 's-1',
    title: 'Escala 12x36 sem intervalo',
    updatedAt: 'Atualizada hoje',
    query: 'trabalhei 12h sem intervalo e sem pagamento de horas extras',
  },
  {
    id: 's-2',
    title: 'Horas in itinere',
    updatedAt: 'Atualizada ha 2 dias',
    query: 'empresa fornecia transporte em trajeto sem transporte publico regular',
  },
])

function removeSearch(id: string) {
  savedSearches.value = savedSearches.value.filter((item) => item.id !== id)
}
</script>

<template>
  <section class="page-stack">
    <header>
      <h1>Buscas salvas</h1>
      <p>Retome pesquisas recentes e acompanhe os insights sem repetir a consulta.</p>
    </header>

    <div v-if="savedSearches.length" class="list">
      <BaseCard v-for="item in savedSearches" :key="item.id">
        <div class="item-head">
          <div>
            <h2>{{ item.title }}</h2>
            <p><Clock3 :size="14" /> {{ item.updatedAt }}</p>
          </div>
          <div class="actions">
            <button type="button" class="ghost"><ExternalLink :size="15" /> Abrir</button>
            <button type="button" class="ghost danger" @click="removeSearch(item.id)">
              <Trash2 :size="15" /> Remover
            </button>
          </div>
        </div>
        <p class="query">{{ item.query }}</p>
      </BaseCard>
    </div>

    <EmptyPanel
      v-else
      title="Nenhuma busca salva"
      description="Salve consultas importantes para acompanhar mudancas de jurisprudencia com rapidez."
    />
  </section>
</template>

<style scoped>
.page-stack {
  display: grid;
  gap: 0.95rem;
}

h1 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
}

header p {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
}

.list {
  display: grid;
  gap: 0.75rem;
}

.item-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

h2 {
  margin: 0;
  color: var(--brand-strong);
  font-size: 1.06rem;
}

.item-head p {
  margin: 0.35rem 0 0;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.query {
  margin: 0.8rem 0 0;
}

.actions {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.ghost {
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  padding: 0.42rem 0.62rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background: var(--bg-surface);
  color: var(--text-body);
  cursor: pointer;
}

.danger {
  color: #8a2334;
  border-color: #e7bcc5;
}

@media (max-width: 740px) {
  .item-head {
    flex-direction: column;
  }
}
</style>
