<script setup lang="ts">
import { QUICK_FILTERS } from '@/shared/constants/mockCases';
import { CalendarClock, CheckCheck, MapPinned } from 'lucide-vue-next';

defineProps<{ activeIds: Set<string> }>()
const emit = defineEmits<{ toggle: [string] }>()

const filterIcons: Record<string, unknown> = {
  procedentes: CheckCheck,
  recentes: CalendarClock,
  recife: MapPinned,
}

function toggle(id: string) {
  emit('toggle', id)
}
</script>

<template>
  <div class="filters-row">
    <span class="label">Filtros rapidos</span>
    <button
      v-for="item in QUICK_FILTERS"
      :key="item.id"
      type="button"
      class="chip"
      :class="{ selected: activeIds.has(item.id) }"
      @click="toggle(item.id)"
    >
      <component :is="filterIcons[item.id]" :size="14" />
      {{ item.label }}
    </button>
  </div>
</template>

<style scoped>
.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  align-items: center;
  margin-top: 0.8rem;
}

.label {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-right: 0.3rem;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  background: var(--bg-surface);
  color: var(--text-body);
  padding: 0.46rem 0.72rem;
  cursor: pointer;
  transition: all 220ms ease;
}

.chip:hover {
  transform: translateY(-1px);
  border-color: var(--brand);
}

.selected {
  border-color: #88a6db;
  background: var(--brand-soft);
  color: var(--brand-strong);
}
</style>
