import HomePage from '@/pages/HomePage/HomePage.vue'
import ProfilePage from '@/pages/ProfilePage/ProfilePage.vue'
import SavedSearchesPage from '@/pages/SavedSearchesPage/SavedSearchesPage.vue'
import SettingsPage from '@/pages/SettingsPage/SettingsPage.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: HomePage },
    { path: '/buscas-salvas', component: SavedSearchesPage },
    { path: '/perfil', component: ProfilePage },
    { path: '/configuracoes', component: SettingsPage },
  ],
})

export default router
