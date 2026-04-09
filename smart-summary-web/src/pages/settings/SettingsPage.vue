<template>
  <div class="settings-page app-page-shell">
    <AppCard>
      <template #header>
        <div>
          <p class="settings-page__eyebrow">SYSTEM SETTINGS</p>
          <h2 class="app-title">系统设置中心</h2>
          <p class="app-subtitle">统一管理基础资料、安全中心与模型配置。</p>
        </div>
      </template>

      <div class="settings-page__tabs">
        <button v-for="tab in tabs" :key="tab.key" :class="['settings-page__tab', { 'settings-page__tab--active': activeTab === tab.key }]" @click="activeTab = tab.key">
          <el-icon><component :is="tab.icon" /></el-icon>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <div class="settings-page__body">
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
          <div class="settings-page__inline-actions">
            <AppButton type="primary" :loading="saving" @click="handleChangePassword">修改密码</AppButton>
          </div>
        </section>

        <section v-else class="settings-page__section">
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
          <div class="settings-page__inline-actions">
            <AppButton @click="handleTestConnection" :loading="saving">测试连通性</AppButton>
          </div>
        </section>
      </div>

      <template #footer>
        <div class="settings-page__footer">
          <AppButton @click="handleClose">取消</AppButton>
          <AppButton type="primary" :loading="saving" @click="handleSave">保存设置</AppButton>
        </div>
      </template>
    </AppCard>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Setting } from '@element-plus/icons-vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import { settingsService } from '@/services/settings.service'
import { ElMessage } from 'element-plus'

const activeTab = ref('info')
const saving = ref(false)
const username = ref('User')
const router = useRouter()
const tabs = [
  { key: 'info', label: '基本信息', icon: User },
  { key: 'security', label: '安全中心', icon: Lock },
  { key: 'model', label: '模型配置', icon: Setting }
]

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
    if (data.success && data.data) Object.assign(form, data.data)
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
</script>

<style scoped>
.settings-page__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.16em;
  color: var(--app-color-text-muted);
}

.settings-page__tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 20px 0;
}

.settings-page__tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: var(--app-panel-bg-soft);
  border: 1px solid var(--app-color-border);
  color: var(--app-color-text-soft);
}

.settings-page__tab--active {
  background: var(--app-color-primary-soft);
  color: var(--app-color-primary-strong);
  border-color: rgba(37, 99, 235, 0.2);
}

.settings-page__body {
  min-height: 0;
}

.settings-page__section {
  padding: 4px 0 0;
}

.settings-page__grid {
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  gap: 24px;
  align-items: stretch;
}

.settings-page__avatar-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 18px;
  min-height: 100%;
  padding: 24px;
  border-radius: var(--app-radius-lg);
  background: linear-gradient(180deg, rgba(37, 99, 235, 0.08), rgba(79, 70, 229, 0.03));
  border: 1px solid var(--app-color-border);
}

.settings-page__avatar {
  width: 84px;
  height: 84px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  box-shadow: 0 18px 36px rgba(37, 99, 235, 0.22);
}

.settings-page__avatar-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.settings-page__avatar-block h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
}

.settings-page__avatar-block p {
  margin: 0;
  color: var(--app-color-text-muted);
  line-height: 1.7;
}

.settings-page__form--info {
  align-self: center;
}

.settings-page__form :deep(.el-form-item__label) {
  color: var(--app-color-text-soft);
  font-weight: 600;
}

.settings-page__footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.settings-page__inline-actions {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 960px) {
  .settings-page__grid {
    grid-template-columns: 1fr;
  }

  .settings-page__avatar-block {
    min-height: auto;
  }
}
</style>
