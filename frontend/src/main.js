import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/main.css'

import UploadPage  from './pages/UploadPage.vue'
import ResultsPage from './pages/ResultsPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',        component: UploadPage,  name: 'upload'  },
    { path: '/results', component: ResultsPage, name: 'results' },
  ]
})

createApp(App).use(router).mount('#app')
