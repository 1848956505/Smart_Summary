<template>
  <div class="generate-page app-page-shell">
    <div class="generate-page__layout">
      <AppCard class="generate-page__panel">
        <template #header>
          <div>
            <p class="generate-page__eyebrow">输入与参数</p>
            <h2 class="app-title">智能生成工作总结</h2>
            <p class="app-subtitle">输入一段工作记录，系统会生成结构化总结、周报或复盘内容。</p>
          </div>
          <AppTag type="primary">支持 Markdown</AppTag>
        </template>

        <div class="generate-page__content">
          <div class="generate-page__toolbar">
            <StyleSelector v-model="form.style" />
            <AppButton type="primary" :loading="generating" :disabled="generating || !form.text.trim()" @click="handleGenerate">
              {{ generating ? 'AI 处理中' : '一键生成' }}
            </AppButton>
          </div>

          <textarea
            v-model="form.text"
            class="generate-page__textarea"
            placeholder="例如：完成了周报系统重构，修复了权限校验问题，梳理了前端工作台布局..."
          />
        </div>
      </AppCard>

      <AppCard class="generate-page__panel" :compact="true">
        <template #header>
          <div>
            <p class="generate-page__eyebrow">生成结果</p>
            <h2 class="app-title">结果预览</h2>
          </div>
          <div class="generate-page__actions">
            <AppButton @click="copyResult" :disabled="!result">复制</AppButton>
            <AppButton @click="exportMarkdown" :disabled="!result">Markdown</AppButton>
            <AppButton @click="exportPDF" :disabled="!result">PDF</AppButton>
          </div>
        </template>

        <div v-if="result" class="generate-page__result scroll-area" v-html="renderedResult"></div>
        <AppEmpty v-else description="生成后会在这里展示结构化结果" />

        <template v-if="result">
          <div class="generate-page__footer">
            <span class="text-muted">结果可继续复制或导出</span>
            <AppButton variant="danger" @click="clearResult">清除结果</AppButton>
          </div>
        </template>
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { marked } from 'marked'
import html2pdf from 'html2pdf.js'
import { ElMessage } from 'element-plus'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTag from '@/components/ui/AppTag.vue'
import AppEmpty from '@/components/ui/AppEmpty.vue'
import StyleSelector from '@/components/StyleSelector.vue'
import { summaryService } from '@/services/summary.service'

const form = reactive({ text: '', style: 'dingtalk' })
const generating = ref(false)
const result = ref('')

const renderedResult = computed(() => (result.value ? marked.parse(result.value) : ''))

const handleGenerate = async () => {
  if (!form.text.trim()) {
    ElMessage.warning('请输入工作记录')
    return
  }
  generating.value = true
  try {
    const { data } = await summaryService.generate({ text: form.text, style: form.style })
    if (data.success) {
      result.value = data.data || ''
      ElMessage.success('生成成功')
    } else {
      ElMessage.error(data.message || '生成失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '生成失败')
  } finally {
    generating.value = false
  }
}

const copyResult = async () => {
  if (!result.value) return
  await navigator.clipboard.writeText(result.value)
  ElMessage.success('已复制')
}

const exportMarkdown = () => {
  if (!result.value) return
  const blob = new Blob([result.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `summary_${new Date().toISOString().slice(0, 10)}.md`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Markdown 已导出')
}

const exportPDF = () => {
  if (!result.value) return
  const temp = document.createElement('div')
  temp.innerHTML = `<pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">${result.value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')}</pre>`
  html2pdf().set({
    margin: 10,
    filename: `summary_${new Date().toISOString().slice(0, 10)}.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  }).from(temp).save()
}

const clearResult = () => {
  result.value = ''
}
</script>

<style scoped>
.generate-page {
  gap: var(--app-space-4);
}

.generate-page__layout {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: var(--app-space-4);
  min-height: 0;
}

.generate-page__panel {
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.generate-page__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.16em;
  color: var(--app-color-text-muted);
}

.generate-page__content {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-4);
  min-height: 0;
}

.generate-page__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--app-space-3);
  flex-wrap: wrap;
}

.generate-page__textarea {
  width: 100%;
  min-height: 420px;
  resize: none;
  padding: 16px;
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-color-border);
  background: var(--app-panel-bg-soft);
  color: var(--app-color-text);
  outline: none;
  line-height: 1.75;
}

.generate-page__textarea:focus {
  border-color: var(--app-color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
}

.generate-page__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.generate-page__result {
  flex: 1;
  min-height: 360px;
  padding: 16px;
  border-radius: var(--app-radius-lg);
  background: var(--app-panel-bg-soft);
  border: 1px solid var(--app-color-border);
  line-height: 1.8;
  color: var(--app-color-text);
}

.generate-page__result :deep(h1) {
  font-size: 22px;
  margin: 16px 0 10px;
}

.generate-page__result :deep(h2) {
  font-size: 18px;
  margin: 14px 0 8px;
}

.generate-page__footer {
  margin-top: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--app-space-3);
}

@media (max-width: 1100px) {
  .generate-page__layout {
    grid-template-columns: 1fr;
  }
}
</style>
