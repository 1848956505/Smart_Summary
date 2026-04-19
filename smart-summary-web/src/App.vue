<template>
  <div class="app-scale-shell">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, provide, reactive } from 'vue'

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

provide('userInfo', { userInfo, setUser, logout })
provide('theme', { currentTheme, setTheme })
</script>

<style scoped>
.app-scale-shell {
  width: 100%;
  min-height: 100%;
}
</style>
