<template>
  <div class="app-scale-shell" :class="themeClass">
    <router-view />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, provide, reactive, watch } from 'vue'
import { themeNames } from '@/constants/theme'

const currentTheme = reactive({ style: 'light' })
const userInfo = reactive({ id: null, username: '', token: '' })

const setUser = (user) => {
  userInfo.id = user.id
  userInfo.username = user.username
  userInfo.token = user.token
  localStorage.setItem('user', JSON.stringify(userInfo))
}

const setTheme = (style) => {
  currentTheme.style = style
  localStorage.setItem('theme', style)
}

const normalizeThemeClass = (themeValue) => {
  const value = String(themeValue || '').trim()
  if (!value || value === 'light' || value === themeNames.light) return themeNames.light
  if (value === 'lightClassic' || value === 'light-classic' || value === themeNames.lightClassic) return themeNames.lightClassic
  if (value === 'dark' || value === themeNames.dark) return themeNames.dark
  return value.startsWith('theme-') ? value : themeNames.light
}

const themeClass = computed(() => normalizeThemeClass(currentTheme.style))
const themeClasses = [themeNames.light, themeNames.lightClassic, themeNames.dark]

const applyThemeClassToBody = (theme) => {
  if (typeof document === 'undefined') return
  document.body.classList.remove(...themeClasses)
  document.body.classList.add(theme)
}

const logout = () => {
  userInfo.id = null
  userInfo.username = ''
  userInfo.token = ''
  localStorage.removeItem('user')
}

onMounted(() => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) Object.assign(userInfo, JSON.parse(savedUser))
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) currentTheme.style = savedTheme
})

watch(
  themeClass,
  (theme) => {
    applyThemeClassToBody(theme)
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (typeof document === 'undefined') return
  document.body.classList.remove(...themeClasses)
})

provide('userInfo', { userInfo, setUser, logout })
provide('theme', { currentTheme, setTheme })
</script>

<style scoped>
.app-scale-shell {
  width: 100%;
  min-height: 100vh;
  background: var(--app-page-bg);
  background-attachment: fixed;
}
</style>
