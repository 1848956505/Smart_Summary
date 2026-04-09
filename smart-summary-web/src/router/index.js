import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import AppLayout from '@/layout/AppLayout.vue'
import DashboardPage from '@/pages/dashboard/DashboardPage.vue'
import GeneratePage from '@/pages/generate/GeneratePage.vue'
import MemosPage from '@/pages/memos/MemosPage.vue'
import HistoryPage from '@/pages/history/HistoryPage.vue'
import SettingsPage from '@/pages/settings/SettingsPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'Login', component: Login },
    { path: '/register', name: 'Register', component: Register },
    { path: '/home', redirect: '/app/dashboard' },
    { path: '/settings', redirect: '/app/settings' },
    {
      path: '/app',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/app/dashboard' },
        { path: 'dashboard', name: 'Dashboard', component: DashboardPage },
        { path: 'generate', name: 'Generate', component: GeneratePage },
        { path: 'memos', name: 'Memos', component: MemosPage },
        { path: 'history', name: 'History', component: HistoryPage },
        { path: 'settings', name: 'SettingsPage', component: SettingsPage }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  if (to.meta.requiresAuth && !user) next('/login')
  else next()
})

export default router
