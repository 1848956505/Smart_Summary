<template>
  <div class="app-layout" :class="themeClass">
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :active-key="activeKey"
      :menu-items="menuItems"
      :username="username"
      :display-username="displayUsername"
      :user-position="userPosition"
      :user-avatar="userAvatar"
      @toggle="sidebarCollapsed = !sidebarCollapsed"
      @select="handleSelect"
      @logout="handleLogout"
      @open-settings="openSettings"
    />

    <div class="app-layout__main">
      <AppHeader :title="pageTitle" :breadcrumb="breadcrumbItems" />
      <AppContent>
        <router-view />
      </AppContent>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import AppContent from './AppContent.vue'
import { appMenu } from '@/constants/menu'
import { appRoutes } from '@/constants/routes'

const router = useRouter()
const route = useRoute()
const sidebarCollapsed = ref(false)

const user = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
})

const username = computed(() => user.value?.username || 'User')
const displayUsername = computed(() => user.value?.username || 'User')
const userPosition = ref('企业协作空间')
const userAvatar = computed(() => (username.value || 'U').slice(0, 1).toUpperCase())

const activeKey = computed(() => {
  if (route.path.startsWith('/app/generate')) return 'generate'
  if (route.path.startsWith('/app/memos')) return 'memos'
  if (route.path.startsWith('/app/history')) return 'history'
  if (route.path.startsWith('/app/settings')) return 'settings'
  return 'dashboard'
})

const pageTitle = computed(() => {
  const titles = {
    dashboard: '工作台',
    generate: '智能生成',
    memos: '碎片记录本',
    history: '历史周报',
    settings: '系统设置'
  }
  return titles[activeKey.value] || '工作台'
})

const breadcrumbItems = computed(() => {
  const trail = [{ label: '工作台', to: appRoutes.dashboard }]
  if (activeKey.value !== 'dashboard') {
    trail.push({ label: pageTitle.value })
  }
  return trail
})

const menuItems = appMenu

const handleSelect = (key) => {
  const target = appRoutes[key] || appRoutes.dashboard
  router.push(target)
}

const handleLogout = () => {
  localStorage.removeItem('user')
  router.push('/login')
}

const openSettings = () => {
  router.push(appRoutes.settings)
}

const themeClass = computed(() => 'theme-light')
</script>

<style scoped>
.app-layout {
  width: 100%;
  height: 100%;
  display: flex;
  gap: var(--app-space-4);
  padding: var(--app-space-4);
  overflow: hidden;
}

.app-layout__main {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: var(--app-radius-2xl);
  background: var(--app-panel-bg);
  border: 1px solid var(--app-panel-border);
  box-shadow: var(--app-panel-shadow);
}
</style>
