<template>
  <div class="min-h-screen flex items-center justify-center p-6 bg-[#f0f0f5] relative overflow-hidden font-sans antialiased">
    <!-- 背景弥散光效 -->
    <div class="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-500/30 rounded-full mix-blend-multiply filter blur-[150px] pointer-events-none"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-purple-500/30 rounded-full mix-blend-multiply filter blur-[150px] pointer-events-none"></div>

    <!-- 注册卡片容器 -->
    <div class="flex w-full max-w-[1000px] h-[650px] bg-white/70 backdrop-blur-2xl rounded-[2.5rem] shadow-[0_20px_60px_-15px_rgba(0,0,0,0.1)] overflow-hidden border border-white/80 relative z-10">
      
      <!-- 左侧：品牌展示区 -->
      <div class="hidden md:flex w-1/2 p-12 flex-col justify-between relative overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 text-white">
        <div class="absolute top-[-10%] left-[-10%] w-64 h-64 bg-white/20 rounded-full filter blur-[60px]"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-80 h-80 bg-blue-400/30 rounded-full filter blur-[80px]"></div>

        <div class="relative z-10">
          <div class="flex items-center gap-3 mb-8">
            <div class="w-10 h-10 rounded-xl bg-white/20 backdrop-blur-md shadow-lg border border-white/30 flex items-center justify-center">
              <span class="text-white text-xl font-extrabold">S</span>
            </div>
            <span class="font-extrabold tracking-tight text-2xl">SmartSummary</span>
          </div>
          
          <h1 class="text-4xl font-bold leading-tight mb-4 tracking-wide">
            加入我们，<br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-200 to-purple-200">
              让工作更高效。
            </span>
          </h1>
          <p class="text-indigo-100 text-sm leading-relaxed max-w-sm">
            一键记录工作碎片，AI 智能生成专业周报，告别繁琐的总结工作。
          </p>
        </div>

        <!-- 装饰卡片 -->
        <div class="relative z-10 bg-white/10 backdrop-blur-md border border-white/20 p-5 rounded-2xl shadow-2xl w-4/5">
          <div class="flex items-center gap-3 mb-3">
            <el-icon class="text-blue-300"><Star /></el-icon>
            <div>
              <div class="text-sm font-bold text-white">智能识别</div>
              <div class="text-[10px] text-indigo-200">自动归纳工作内容 · AI 润色</div>
            </div>
          </div>
          <div class="space-y-2">
            <div class="h-2 bg-white/20 rounded-full w-full"></div>
            <div class="h-2 bg-white/20 rounded-full w-2/3"></div>
          </div>
        </div>
      </div>

      <!-- 右侧：注册表单 -->
      <div class="w-full md:w-1/2 p-10 sm:p-14 flex flex-col justify-center bg-white/40">
        <div class="max-w-sm w-full mx-auto">
          <div class="text-center mb-8">
            <h2 class="text-2xl font-extrabold text-gray-800 mb-2">创建账号</h2>
            <p class="text-sm text-gray-500 font-medium">开始你的智能工作记录之旅</p>
          </div>

          <el-form :model="form" :rules="rules" ref="formRef" class="space-y-4">
            <!-- 用户名 -->
            <div class="space-y-1.5">
              <label class="text-[13px] font-bold text-gray-700 ml-1">用户名</label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <el-icon class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"><User /></el-icon>
                </div>
                <el-input 
                  v-model="form.username" 
                  placeholder="请输入用户名"
                  class="!bg-white/80 !border-gray-200/80 !rounded-2xl !pl-11 !py-3 !text-sm"
                />
              </div>
            </div>

            <!-- 邮箱 -->
            <div class="space-y-1.5">
              <label class="text-[13px] font-bold text-gray-700 ml-1">邮箱</label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <el-icon class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"><Message /></el-icon>
                </div>
                <el-input 
                  v-model="form.email" 
                  placeholder="example@company.com"
                  class="!bg-white/80 !border-gray-200/80 !rounded-2xl !pl-11 !py-3 !text-sm"
                />
              </div>
            </div>

            <!-- 密码 -->
            <div class="space-y-1.5">
              <label class="text-[13px] font-bold text-gray-700 ml-1">密码</label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <el-icon class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"><Lock /></el-icon>
                </div>
                <el-input 
                  v-model="form.password" 
                  type="password" 
                  placeholder="至少6位"
                  class="!bg-white/80 !border-gray-200/80 !rounded-2xl !pl-11 !py-3 !text-sm"
                />
              </div>
            </div>

            <!-- 确认密码 -->
            <div class="space-y-1.5">
              <label class="text-[13px] font-bold text-gray-700 ml-1">确认密码</label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <el-icon class="h-5 w-5 text-gray-400 group-focus-within:text-blue-500 transition-colors"><Lock /></el-icon>
                </div>
                <el-input 
                  v-model="form.confirmPassword" 
                  type="password" 
                  placeholder="再次输入密码"
                  class="!bg-white/80 !border-gray-200/80 !rounded-2xl !pl-11 !py-3 !text-sm"
                  @keyup.enter="handleRegister"
                />
              </div>
            </div>

            <!-- 注册按钮 -->
            <el-button 
              type="primary" 
              size="large" 
              :loading="loading" 
              class="w-full !bg-gradient-to-r !from-blue-600 !via-indigo-600 !to-purple-600 !text-white !text-[15px] !font-bold !rounded-2xl !shadow-lg !shadow-indigo-500/30 hover:!shadow-indigo-500/50 !transform !transition hover:!-translate-y-0.5 !mt-6"
              @click="handleRegister"
            >
              <span class="relative flex items-center gap-2">
                立即注册
                <el-icon><ArrowRight /></el-icon>
              </span>
            </el-button>
          </el-form>

          <p class="mt-6 text-center text-[13px] text-gray-500">
            已有账号？
            <router-link to="/login" class="font-bold text-blue-600 hover:text-blue-700 transition">
              立即登录
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
import { User, Lock, Message, ArrowRight, Star } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度至少6位'))
  } else {
    if (form.confirmPassword !== '') {
      formRef.value.validateField('confirmPassword')
    }
    callback()
  }
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [{ validator: validatePass, trigger: 'blur' }],
  confirmPassword: [{ validator: validatePass2, trigger: 'blur' }]
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const { data } = await axios.post('/api/auth/register', {
        username: form.username,
        password: form.password,
        email: form.email
      })
      
      if (data.success) {
        ElMessage.success('注册成功！请登录')
        router.push('/login')
      } else {
        ElMessage.error(data.message || '注册失败')
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '注册失败，请检查网络')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
:deep(.el-input__wrapper) {
  box-shadow: 0 2px 10px -3px rgba(0,0,0,0.02);
  transition: all 0.3s;
}
:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 15px -3px rgba(0,0,0,0.06);
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 20px -3px rgba(59, 130, 246, 0.15) !important;
}
</style>