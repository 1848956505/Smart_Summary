<template>
  <div class="auth-page min-h-screen flex items-center justify-center p-6 font-sans antialiased text-gray-800 relative overflow-hidden">
    <!-- 背景弥散光效 -->
    <div class="auth-orb auth-orb--left absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full mix-blend-multiply filter blur-[150px] pointer-events-none"></div>
    <div class="auth-orb auth-orb--right absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full mix-blend-multiply filter blur-[150px] pointer-events-none"></div>

    <!-- 登录卡片容器 -->
    <div class="auth-card flex w-full max-w-[1000px] h-[600px] backdrop-blur-2xl rounded-[2.5rem] overflow-hidden relative z-10">
      
      <!-- 左侧：品牌与视觉展示区 -->
      <div class="auth-brand-panel hidden md:flex w-1/2 p-12 flex-col justify-between relative overflow-hidden text-white">
        <div class="auth-brand-glow absolute top-[-10%] left-[-10%] w-64 h-64 rounded-full filter blur-[60px]"></div>
        <div class="auth-brand-glow absolute bottom-[-10%] right-[-10%] w-80 h-80 rounded-full filter blur-[80px]"></div>

        <div class="relative z-10">
          <div class="flex items-center gap-3 mb-8">
            <div class="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md shadow-lg border border-white/30 flex items-center justify-center">
              <span class="text-white text-xl font-extrabold">S</span>
            </div>
            <span class="font-extrabold tracking-tight text-2xl">SmartSummary</span>
          </div>
          
          <h1 class="text-4xl font-bold leading-tight mb-4 tracking-wide">
            一键告别繁琐，<br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-200 to-purple-200">
              让 AI 执笔你的工作。
            </span>
          </h1>
          <p class="text-indigo-100 text-sm leading-relaxed max-w-sm">
            通过时间轴记录日常碎片，利用大语言模型自动生成专业、结构化的职场总结与周报。
          </p>
        </div>

        <!-- 装饰卡片 -->
        <div class="relative z-10 animate-float bg-white/10 backdrop-blur-md border border-white/20 p-5 rounded-2xl shadow-2xl w-4/5">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-8 h-8 rounded-full bg-green-400/20 flex items-center justify-center">
              <el-icon class="text-green-300"><SuccessFilled /></el-icon>
            </div>
            <div>
              <div class="text-sm font-bold text-white">报告生成成功</div>
              <div class="text-[10px] text-indigo-200">飞书风格 · 耗时 2.4s</div>
            </div>
          </div>
          <div class="space-y-2">
            <div class="h-2 bg-white/20 rounded-full w-3/4"></div>
            <div class="h-2 bg-white/20 rounded-full w-1/2"></div>
          </div>
        </div>
      </div>

      <!-- 右侧：交互表单区 -->
      <div class="auth-form-panel w-full md:w-1/2 p-10 sm:p-14 flex flex-col justify-center">
        <div class="max-w-sm w-full mx-auto">
          <div class="text-center mb-10">
            <h2 class="text-2xl font-extrabold text-gray-800 mb-2">欢迎回来</h2>
            <p class="text-sm text-gray-500 font-medium">登录以继续访问你的工作台</p>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-6">
            <!-- 账号输入框 -->
            <div class="space-y-1.5">
              <label class="text-[13px] font-bold text-gray-700 ml-1">邮箱 / 用户名</label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <el-icon class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"><User /></el-icon>
                </div>
                <input 
                  v-model="form.username" 
                  type="text" 
                  placeholder="example@company.com" 
                  class="auth-input w-full rounded-2xl pl-11 pr-4 py-3.5 text-sm focus:outline-none transition-all"
                >
              </div>
            </div>

            <!-- 密码输入框 -->
            <div class="space-y-1.5">
              <label class="text-[13px] font-bold text-gray-700 ml-1">密码</label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <el-icon class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"><Lock /></el-icon>
                </div>
                <input 
                  v-model="form.password" 
                  type="password" 
                  placeholder="••••••••" 
                  class="auth-input w-full rounded-2xl pl-11 pr-10 py-3.5 text-sm focus:outline-none transition-all"
                  @keyup.enter="handleLogin"
                >
                <div class="absolute inset-y-0 right-0 pr-4 flex items-center">
                  <a href="#" class="auth-link text-[12px] font-bold transition">忘记?</a>
                </div>
              </div>
            </div>

            <!-- 登录按钮 -->
            <button 
              type="submit" 
              :disabled="loading"
              class="auth-cta group relative w-full flex justify-center py-3.5 px-4 text-white text-[15px] font-bold rounded-2xl transform transition hover:-translate-y-0.5 overflow-hidden mt-8 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div class="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
              <span class="relative flex items-center gap-2">
                <el-icon v-if="loading" class="animate-spin"><Loading /></el-icon>
                <span v-else>立即登录</span>
                <el-icon v-if="!loading"><ArrowRight /></el-icon>
              </span>
            </button>
          </form>

          <p class="mt-8 text-center text-[13px] text-gray-500">
            还没有账号？
            <router-link to="/register" class="auth-link font-bold transition relative after:content-[''] after:absolute after:w-full after:scale-x-0 after:h-[2px] after:bottom-0 after:left-0 after:origin-bottom-right after:transition-transform hover:after:scale-x-100 hover:after:origin-bottom-left">
              免费注册
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, ArrowRight, Loading, SuccessFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  
  loading.value = true
  try {
    const { data } = await axios.post('/api/auth/login', {
      username: form.username,
      password: form.password
    })
    
    if (data.success) {
      localStorage.setItem('user', JSON.stringify({
        id: data.data.id,
        username: data.data.username,
        token: ''
      }))
      ElMessage.success('登录成功！')
      router.push('/home')
    } else {
      ElMessage.error(data.message || '登录失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '登录失败，请检查网络')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  background: var(--app-page-bg);
}

.auth-orb--left {
  background: var(--auth-bg-orb-left);
}

.auth-orb--right {
  background: var(--auth-bg-orb-right);
}

.auth-card {
  background: var(--auth-panel-bg);
  border: 1px solid var(--app-panel-border);
  box-shadow: var(--app-panel-shadow);
}

.auth-brand-panel {
  background: var(--auth-brand-gradient);
}

.auth-brand-glow {
  background: var(--auth-brand-glow);
}

.auth-form-panel {
  background: var(--auth-form-bg);
}

.auth-input {
  background: var(--auth-input-bg);
  border: 1px solid var(--auth-input-border);
  color: var(--app-color-text);
  box-shadow: 0 2px 10px -3px rgba(0, 0, 0, 0.02);
}

.auth-input::placeholder {
  color: var(--app-color-text-muted);
}

.auth-input:focus {
  border-color: var(--app-accent-border-strong);
  box-shadow: 0 0 0 4px var(--auth-input-ring);
  background: var(--auth-input-bg-focus);
}

.auth-cta {
  background-image: var(--app-gradient-primary);
  box-shadow: var(--app-shadow-soft-lg);
}

.auth-cta:hover {
  background-image: var(--app-gradient-primary-hover);
}

.auth-link {
  color: var(--app-color-primary);
}

.auth-link:hover {
  color: var(--app-color-primary-strong);
}

.auth-link::after {
  background: currentColor;
}

@keyframes shimmer {
  100% { transform: translateX(100%); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.animate-float {
  animation: float 6s ease-in-out infinite;
}
</style>
