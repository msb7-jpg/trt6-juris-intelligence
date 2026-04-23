<script setup lang="ts">
import BaseCard from '@/shared/components/ui/BaseCard.vue'
import { Bell, Globe2, ShieldCheck } from 'lucide-vue-next'
import { ref } from 'vue'

const language = ref('pt-BR')
const notifications = ref(true)
const highContrast = ref(false)
</script>

<template>
  <section class="page-stack">
    <header>
      <h1>Configuracoes</h1>
      <p>Preferencias essenciais para experiencia juridica personalizada.</p>
    </header>

    <BaseCard>
      <h2><Globe2 :size="16" /> Idioma</h2>
      <select v-model="language">
        <option value="pt-BR">Portugues (Brasil)</option>
        <option value="en-US">English (US)</option>
      </select>
    </BaseCard>

    <BaseCard>
      <h2><Bell :size="16" /> Notificacoes</h2>
      <label>
        <input v-model="notifications" type="checkbox" />
        Receber alertas de mudanca jurisprudencial nas buscas salvas.
      </label>
    </BaseCard>

    <BaseCard>
      <h2><ShieldCheck :size="16" /> Privacidade visual</h2>
      <label>
        <input v-model="highContrast" type="checkbox" />
        Ativar contraste elevado para leitura de documentos extensos.
      </label>
    </BaseCard>
  </section>
</template>

<style scoped>
.page-stack {
  display: grid;
  gap: 0.95rem;
}

h1,
h2 {
  margin: 0;
  font-family: var(--font-display);
  color: var(--text-strong);
}

header p {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
}

h2 {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 1rem;
}

select {
  margin-top: 0.65rem;
  min-width: 240px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  min-height: 40px;
  padding: 0 0.75rem;
}

label {
  margin-top: 0.65rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-body);
}
</style>
