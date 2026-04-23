<template>
  <div class="settings-page app-page-shell">
    <div class="settings-page__shell">
      <aside class="settings-page__nav app-surface">
        <div class="settings-page__nav-head">
          <p class="settings-page__eyebrow">SETTINGS</p>
          <h2 class="app-title">系统设置</h2>
          <p class="app-subtitle">统一管理账户、安全与模型配置。</p>
        </div>

        <div class="settings-page__tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            :class="['settings-page__tab', { 'settings-page__tab--active': activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            <el-icon><component :is="tab.icon" /></el-icon>
            <span>{{ tab.label }}</span>
          </button>
        </div>

        <div class="settings-page__nav-foot">
          <p>最近保存</p>
          <strong>{{ lastSavedText }}</strong>
        </div>
      </aside>

      <section class="settings-page__workspace">
        <header class="settings-page__context app-surface">
          <div class="settings-page__context-copy">
            <p class="settings-page__context-label">{{ activeTabConfig.eyebrow }}</p>
            <h3 class="app-title">{{ activeTabConfig.title }}</h3>
            <p class="app-subtitle">{{ activeTabConfig.description }}</p>
          </div>

          <div class="settings-page__context-actions">
            <span class="memo-chip memo-chip--soft">{{ activeTabConfig.label }}</span>
            <AppButton v-if="activeTab === 'model'" :loading="saving" @click="handleTestConnection">测试连通性</AppButton>
            <AppButton v-if="activeTab === 'security'" type="primary" :loading="saving" @click="handleChangePassword">修改密码</AppButton>
          </div>
        </header>

        <section class="settings-page__panel app-surface">
          <div class="settings-page__body scroll-area">
            <section v-if="activeTab === 'info'" class="settings-page__section">
              <div class="settings-page__grid">
                <div class="settings-page__avatar-block">
                  <div class="settings-page__avatar">{{ username.slice(0, 1).toUpperCase() }}</div>
                  <div class="settings-page__avatar-copy">
                    <h3>基本信息</h3>
                    <p>头像、用户名、邮箱与岗位信息。</p>
                  </div>
                </div>

                <el-form label-position="top" :model="form" class="settings-page__form settings-page__form--info">
                  <el-form-item label="用户名">
                    <el-input v-model="form.username" />
                  </el-form-item>
                  <el-form-item label="邮箱">
                    <el-input v-model="form.email" />
                  </el-form-item>
                  <el-form-item label="岗位">
                    <el-input v-model="form.position" />
                  </el-form-item>
                </el-form>
              </div>
            </section>

            <section v-else-if="activeTab === 'security'" class="settings-page__section">
              <el-form label-position="top" :model="passwordForm" class="settings-page__form">
                <el-form-item label="原密码"><el-input v-model="passwordForm.oldPassword" type="password" /></el-form-item>
                <el-form-item label="新密码"><el-input v-model="passwordForm.newPassword" type="password" /></el-form-item>
                <el-form-item label="确认新密码"><el-input v-model="passwordForm.confirmPassword" type="password" /></el-form-item>
              </el-form>
            </section>

            <section v-else class="settings-page__section">
              <div class="settings-page__theme-switch">
                <p class="settings-page__theme-label">界面主题</p>
                <div class="settings-page__theme-options">
                  <button
                    v-for="option in themeOptions"
                    :key="option.value"
                    type="button"
                    :class="['settings-page__theme-option', { 'settings-page__theme-option--active': selectedThemeKey === option.value }]"
                    @click="handleThemeChange(option.value)"
                  >
                    <span class="settings-page__theme-dot" :style="{ background: option.preview }"></span>
                    <span>{{ option.label }}</span>
                  </button>
                </div>
              </div>

              <el-form label-position="top" :model="form" class="settings-page__form">
                <el-form-item label="Model ID"><el-input v-model="form.modelId" /></el-form-item>
                <el-form-item label="API Key"><el-input v-model="form.apiKey" type="password" /></el-form-item>
                <el-form-item label="Base URL"><el-input v-model="form.baseUrl" /></el-form-item>
                <el-form-item label="Temperature">
                  <el-slider v-model="form.temperature" :min="0" :max="1.5" :step="0.1" />
                </el-form-item>
                <el-form-item label="Max Tokens">
                  <el-slider v-model="form.maxTokens" :min="512" :max="4096" :step="128" />
                </el-form-item>
              </el-form>
            </section>
          </div>
        </section>

        <footer class="settings-page__footer app-surface">
          <div class="settings-page__footer-actions">
            <AppButton @click="handleClose">取消</AppButton>
            <AppButton type="primary" :loading="saving" @click="handleSave">保存设置</AppButton>
          </div>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Setting } from '@element-plus/icons-vue'
import AppButton from '@/components/ui/AppButton.vue'
import { settingsService } from '@/services/settings.service'
import { ElMessage } from 'element-plus'
import { themeNames } from '@/constants/theme'

const activeTab = ref('info')
const saving = ref(false)
const username = ref('User')
const lastSavedAt = ref(null)
const router = useRouter()
const themeState = inject('theme', null)

const tabs = [
  {
    key: 'info',
    label: '基本信息',
    icon: User,
    eyebrow: 'PROFILE',
    title: '基础资料',
    description: '维护用户名、邮箱与岗位信息。'
  },
  {
    key: 'security',
    label: '安全中心',
    icon: Lock,
    eyebrow: 'SECURITY',
    title: '账户安全',
    description: '更新登录密码并保持账户安全。'
  },
  {
    key: 'model',
    label: '模型配置',
    icon: Setting,
    eyebrow: 'MODEL',
    title: '模型与接口',
    description: '配置模型参数并测试 API 连通性。'
  }
]

const activeTabConfig = computed(() => tabs.find((tab) => tab.key === activeTab.value) || tabs[0])

const themeOptions = [
  {
    label: '经典蓝',
    value: themeNames.lightClassic,
    preview: 'linear-gradient(90deg, #2563eb, #60a5fa)'
  },
  {
    label: '紫色玻璃',
    value: themeNames.light,
    preview: 'linear-gradient(90deg, #4f46e5, #a855f7)'
  }
]

const selectedThemeKey = computed(() => {
  const value = themeState?.currentTheme?.style || localStorage.getItem('theme') || themeNames.light
  if (value === 'lightClassic' || value === 'light-classic') return themeNames.lightClassic
  if (value === 'light' || value === themeNames.light) return themeNames.light
  return value
})

const lastSavedText = computed(() => {
  if (!lastSavedAt.value) return '未保存'
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }).format(lastSavedAt.value)
})

const form = reactive({
  username: '',
  email: '',
  position: '',
  modelId: 'qwen2.5-7b-instruct',
  apiKey: '',
  baseUrl: 'http://localhost:8000',
  temperature: 0.7,
  maxTokens: 2048
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

onMounted(async () => {
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  username.value = user?.username || 'User'
  form.username = user?.username || 'User'
  try {
    const { data } = await settingsService.get()
    if (data.success && data.data) {
      Object.assign(form, data.data)
      lastSavedAt.value = new Date()
    }
  } catch {
    // keep defaults if API unavailable
  }
})

const handleClose = () => {
  router.push('/app/dashboard')
}

const handleSave = async () => {
  saving.value = true
  try {
    await settingsService.save(form)
    lastSavedAt.value = new Date()
    ElMessage.success('设置已保存')
  } finally {
    saving.value = false
  }
}

const handleChangePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.warning('请填写完整密码信息')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次新密码不一致')
    return
  }
  saving.value = true
  try {
    await settingsService.changePassword(passwordForm)
    ElMessage.success('密码已修改')
  } finally {
    saving.value = false
  }
}

const handleTestConnection = async () => {
  saving.value = true
  try {
    await settingsService.testConnection(form)
    ElMessage.success('连通性正常')
  } finally {
    saving.value = false
  }
}

const handleThemeChange = (themeValue) => {
  if (!themeValue || selectedThemeKey.value === themeValue) return
  if (themeState?.setTheme) {
    themeState.setTheme(themeValue)
  } else {
    localStorage.setItem('theme', themeValue)
  }
  ElMessage.success(`已切换为${themeValue === themeNames.lightClassic ? '经典蓝' : '紫色玻璃'}主题`)
}
</script>

<style scoped>
.settings-page {
  flex: 1;
  min-height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  overflow: hidden;
}

.settings-page__shell {
  height: 100%;
  display: grid;
  grid-template-columns: minmax(196px, 236px) minmax(0, 1fr);
  gap: var(--app-space-4);
}

.settings-page__nav,
.settings-page__context,
.settings-page__panel,
.settings-page__footer {
  border-radius: var(--app-radius-xl);
  border: 1px solid var(--app-border-soft);
  background: rgba(255, 255, 255, 0.82);
}

.settings-page__nav {
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: var(--app-space-4);
  gap: var(--app-space-4);
}

.settings-page__nav-head {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-2);
}

.settings-page__eyebrow {
  margin: 0;
  font-size: var(--app-type-helper-size);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.settings-page__tabs {
  display: grid;
  gap: 8px;
}

.settings-page__tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  border-radius: var(--app-radius-md);
  border: 1px solid var(--app-border-strong);
  background: var(--app-surface-soft);
  color: var(--app-color-text-soft);
  text-align: left;
}

.settings-page__tab--active {
  background: var(--app-accent-soft-strong);
  color: var(--app-color-primary-strong);
  border-color: var(--app-accent-border);
}

.settings-page__nav-foot {
  margin-top: auto;
  border-top: 1px solid var(--app-color-border-soft);
  padding-top: var(--app-space-4);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.settings-page__nav-foot p {
  margin: 0;
  color: var(--app-color-text-muted);
  font-size: var(--app-type-helper-size);
}

.settings-page__nav-foot strong {
  color: var(--app-color-text-strong);
  font-size: var(--app-type-body-sm-size);
}

.settings-page__workspace {
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: var(--app-space-4);
}

.settings-page__context {
  padding: var(--app-space-4) var(--app-space-5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--app-space-4);
  box-shadow: 0 6px 14px rgba(39, 72, 124, 0.026);
}

.settings-page__context-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.settings-page__context-label {
  margin: 0;
  font-size: var(--app-type-helper-size);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.settings-page__context-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.settings-page__panel {
  flex: 1;
  min-height: 0;
  display: flex;
  overflow: hidden;
}

.settings-page__body {
  width: 100%;
  min-height: 0;
  overflow: auto;
  padding: var(--app-space-5);
}

.settings-page__form :deep(.el-input__wrapper),
.settings-page__form :deep(.el-textarea__inner) {
  border-radius: var(--app-radius-md);
  box-shadow: none;
  border: 1px solid var(--app-border-default);
  background: var(--app-surface-elevated-strong);
}

.settings-page__form :deep(.el-input__wrapper.is-focus),
.settings-page__form :deep(.el-textarea__inner:focus) {
  border-color: var(--app-accent-border-strong);
  box-shadow: 0 0 0 3px var(--app-accent-soft);
}

.settings-page__section {
  min-height: 100%;
}

.settings-page__theme-switch {
  margin-bottom: var(--app-space-5);
  display: flex;
  flex-direction: column;
  gap: var(--app-space-3);
}

.settings-page__theme-label {
  margin: 0;
  font-size: var(--app-type-helper-size);
  font-weight: var(--app-type-weight-semibold);
  color: var(--app-color-text-soft);
}

.settings-page__theme-options {
  display: flex;
  gap: var(--app-space-3);
  flex-wrap: wrap;
}

.settings-page__theme-option {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--app-border-default);
  background: var(--app-surface-elevated-strong);
  color: var(--app-color-text-soft);
  border-radius: 999px;
  padding: 7px 12px;
}

.settings-page__theme-option--active {
  border-color: var(--app-accent-border);
  background: var(--app-accent-soft);
  color: var(--app-color-primary-strong);
}

.settings-page__theme-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.68);
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.06);
}

.settings-page__grid {
  display: grid;
  grid-template-columns: minmax(236px, 312px) minmax(0, 1fr);
  gap: var(--app-space-6);
  align-items: stretch;
}

.settings-page__avatar-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: var(--app-space-5);
  min-height: 100%;
  padding: var(--app-space-6);
  border-radius: var(--app-radius-lg);
  background: linear-gradient(180deg, var(--app-accent-soft), color-mix(in srgb, var(--app-accent-soft) 38%, transparent));
  border: 1px solid var(--app-color-border);
}

.settings-page__avatar {
  width: calc(84px * var(--app-scale));
  height: calc(84px * var(--app-scale));
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: calc(28px * var(--app-scale));
  font-weight: 800;
  background: var(--app-gradient-primary);
  box-shadow: 0 18px 36px color-mix(in srgb, var(--app-color-primary) 30%, transparent);
}

.settings-page__avatar-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.settings-page__avatar-copy h3 {
  margin: 0;
  font-size: var(--app-type-body-size);
  font-weight: var(--app-type-weight-bold);
}

.settings-page__avatar-copy p {
  margin: 0;
  color: var(--app-color-text-muted);
  line-height: var(--app-type-body-line-height);
}

.settings-page__form--info {
  align-self: center;
}

.settings-page__form :deep(.el-form-item__label) {
  color: var(--app-color-text-soft);
  font-weight: var(--app-type-weight-semibold);
}

.settings-page__footer {
  padding: var(--app-space-3) var(--app-space-5);
}

.settings-page__footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 1140px) {
  .settings-page__shell {
    grid-template-columns: minmax(0, 1fr);
  }

  .settings-page__nav {
    padding: var(--app-space-3);
  }

  .settings-page__tabs {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .settings-page__nav-foot {
    margin-top: 0;
  }
}

@media (max-width: 860px) {
  .settings-page__context {
    flex-direction: column;
    align-items: stretch;
  }

  .settings-page__context-actions {
    justify-content: flex-start;
  }

  .settings-page__grid {
    grid-template-columns: 1fr;
  }

  .settings-page__tabs {
    grid-template-columns: 1fr;
  }
}
</style>

