<template>
  <div class="app-layout" :class="[themeClass, { 'app-layout--stacked': isStackedLayout }]">
    <AppSidebar
      :collapsed="sidebarCollapsed"
      :active-key="activeKey"
      :menu-items="menuItems"
      :display-username="displayUsername"
      :user-position="userPosition"
      :user-avatar="userAvatar"
      @toggle="sidebarCollapsed = !sidebarCollapsed"
      @select="handleSelect"
      @logout="handleLogout"
      @open-settings="openSettings"
    />

    <div class="app-layout__main">
      <AppContent :content-width="contentWidth" :full-bleed="isFullBleed">
        <router-view />
      </AppContent>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppContent from './AppContent.vue'
import { appMenu } from '@/constants/menu'
import { appRoutes } from '@/constants/routes'
import { themeNames } from '@/constants/theme'

const router = useRouter()
const route = useRoute()
const sidebarCollapsed = ref(false)
const themeState = inject('theme', null)
const userState = inject('userInfo', null)

const getStoredUser = () => {
  try {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  } catch {
    return null
  }
}

const getStoredTheme = () => {
  try {
    return localStorage.getItem('theme') || 'light'
  } catch {
    return 'light'
  }
}

const normalizeThemeClass = (themeValue) => {
  const value = String(themeValue || '').trim()
  if (!value || value === 'light' || value === themeNames.light) return themeNames.light
  if (value === 'lightClassic' || value === 'light-classic' || value === themeNames.lightClassic) return themeNames.lightClassic
  if (value === 'dark' || value === themeNames.dark) return themeNames.dark
  return value.startsWith('theme-') ? value : themeNames.light
}

const user = computed(() => {
  const injectedUser = userState?.userInfo
  if (injectedUser && (injectedUser.username || injectedUser.id || injectedUser.token)) {
    return injectedUser
  }
  return getStoredUser()
})

const displayUsername = computed(() => user.value?.username || '用户')
const userPosition = computed(() => user.value?.position || user.value?.role || '企业协作空间')
const userAvatar = computed(() => displayUsername.value.slice(0, 1).toUpperCase())

const activeKey = computed(() => route.meta?.navKey || 'dashboard')
const isStackedLayout = computed(() => Boolean(route.meta?.fullBleed))
const contentWidth = computed(() => route.meta?.contentWidth || 'standard')
const isFullBleed = computed(() => Boolean(route.meta?.fullBleed))
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

const themeClass = computed(() => normalizeThemeClass(themeState?.currentTheme?.style || getStoredTheme()))
</script>

<style scoped>
.app-layout {
  width: 100%;
  min-height: 100vh;
  display: flex;
  gap: var(--app-space-5);
  padding: var(--app-shell-gutter);
  overflow: visible;
  background: transparent;
}

.app-layout__main {
  flex: 1;
  min-width: 0;
  min-height: calc(100vh - (var(--app-shell-gutter) * 2));
  display: flex;
  flex-direction: column;
  overflow: visible;
  background: transparent;
  border: 0;
  box-shadow: none;
}

@media (max-width: 1200px) {
  .app-layout {
    flex-direction: column;
    overflow: visible;
  }

  .app-layout--stacked {
    gap: var(--app-space-4);
  }

  .app-layout__main {
    width: 100%;
  }
}
</style>
