<script setup lang="ts">
import { BookmarkCheck, Home, Settings, UserRound } from 'lucide-vue-next'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const links = [
  { to: '/', label: 'Principal', icon: Home },
  { to: '/buscas-salvas', label: 'Buscas salvas', icon: BookmarkCheck },
  { to: '/perfil', label: 'Perfil', icon: UserRound },
  { to: '/configuracoes', label: 'Configuracoes', icon: Settings },
]

const activePath = computed(() => route.path)
</script>

<template>
  <header class="navbar">
    <div class="brand">JusTRT6</div>
    <nav class="nav-items">
      <RouterLink
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="nav-link"
        :class="{ 'is-active': activePath === link.to }"
      >
        <component :is="link.icon" :size="16" />
        <span>{{ link.label }}</span>
      </RouterLink>
    </nav>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 30;
  margin: 1rem auto 0;
  width: min(1220px, calc(100% - 2.5rem));
  padding: 0.8rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-soft);
}

.brand {
  font-family: var(--font-display);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--brand-strong);
  font-size: 1.28rem;
  padding: 0.2rem 0.6rem;
}

.nav-items {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 0.85rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-muted);
  transition: all 220ms ease;
}

.nav-link:hover {
  color: var(--brand-strong);
  background: var(--bg-soft);
}

.is-active {
  background: var(--brand-soft);
  color: var(--brand-strong);
}

@media (max-width: 840px) {
  .navbar {
    width: calc(100% - 1.4rem);
    border-radius: var(--radius-md);
  }

  .brand {
    display: none;
  }

  .nav-items {
    width: 100%;
    justify-content: space-between;
  }

  .nav-link {
    justify-content: center;
    flex: 1 1 auto;
    min-width: 120px;
  }
}
</style>
