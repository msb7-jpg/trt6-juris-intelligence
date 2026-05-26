import { VueQueryPlugin } from '@tanstack/vue-query'
import { MotionPlugin } from '@vueuse/motion'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

import '@/shared/styles/main.css'
import {
  QUERY_DEFAULT_RETRY,
  QUERY_STALE_TIME_MS,
} from '@/shared/constants/api'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(MotionPlugin)
app.use(VueQueryPlugin, {
  queryClientConfig: {
    defaultOptions: {
      queries: {
        staleTime: QUERY_STALE_TIME_MS,
        retry: QUERY_DEFAULT_RETRY,
        refetchOnWindowFocus: false,
      },
    },
  },
})

app.component('Apexchart', VueApexCharts)

app.mount('#app')
