<script setup lang="ts">
import BaseCard from '@/shared/components/ui/BaseCard.vue';
import { BadgeCheck, Building2, Mail, UserRound } from 'lucide-vue-next';
</script>

<template>
  <section class="page-stack">
    <header>
      <h1>Perfil do usuario</h1>
      <p>Gestao de identidade e contexto profissional usado nas analises.</p>
    </header>

    <BaseCard>
      <div class="profile-head">
        <div class="avatar">
          <UserRound :size="24" />
        </div>
        <div>
          <h2>Miguel Batista</h2>
          <p><BadgeCheck :size="14" /> Conta verificada</p>
        </div>
      </div>
      <ul>
        <li><Mail :size="15" /> miguel@example.com</li>
        <li><Building2 :size="15" /> Advocacia Trabalhista - PE</li>
      </ul>
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

.profile-head {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  border: 1px solid var(--line);
  display: grid;
  place-items: center;
  color: var(--brand);
  background: var(--brand-soft);
}

.profile-head p {
  margin: 0.35rem 0 0;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--text-muted);
}

ul {
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.55rem;
}

li {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
</style>
