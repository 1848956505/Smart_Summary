import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import AppLayout from '@/layout/AppLayout.vue'
import DashboardPage from '@/pages/dashboard/DashboardPage.vue'
import GeneratePage from '@/pages/generate/GeneratePage.vue'
import MemosPage from '@/pages/memos/MemosPage.vue'
import HistoryPage from '@/pages/history/HistoryPage.vue'
import SettingsPage from '@/pages/settings/SettingsPage.vue'

const getStoredUser = () => {
  try {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  } catch {
    return null
  }
}

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
        { path: 'dashboard', name: 'Dashboard', component: DashboardPage, meta: { navKey: 'dashboard', contentWidth: 'workspace', fullBleed: true } },
        { path: 'generate', name: 'Generate', component: GeneratePage, meta: { navKey: 'generate', contentWidth: 'workspace', fullBleed: true } },
        { path: 'memos', name: 'Memos', component: MemosPage, meta: { navKey: 'memos', contentWidth: 'workspace', fullBleed: true } },
        { path: 'history', name: 'History', component: HistoryPage, meta: { navKey: 'history', contentWidth: 'workspace' } },
        { path: 'settings', name: 'SettingsPage', component: SettingsPage, meta: { navKey: 'settings', contentWidth: 'standard' } }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const user = getStoredUser()
  if (to.meta.requiresAuth && !user) next('/login')
  else next()
})

export default router
