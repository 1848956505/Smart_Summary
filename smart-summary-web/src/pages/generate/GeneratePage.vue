<template>
  <div class="generate-page app-page-shell">
    <header class="generate-page__topbar app-surface">
      <div class="generate-page__topbar-copy">
        <h2 class="app-title">智能生成工作台</h2>
      </div>

      <div class="generate-page__topbar-actions">
        <span class="memo-chip memo-chip--info">{{ currentStyleLabel }}</span>
        <span :class="['memo-chip', statusChipClass]">{{ statusText }}</span>
        <AppButton v-if="result" @click="copyResult">复制</AppButton>
        <AppButton v-if="result" @click="exportMarkdown">Markdown</AppButton>
        <AppButton v-if="result" @click="exportPDF">PDF</AppButton>
        <AppButton v-if="result" variant="danger" @click="clearResult">清除结果</AppButton>
      </div>
    </header>

    <section class="generate-page__stage">
      <div class="generate-page__stage-scroll scroll-area">
        <div v-if="generating" class="generate-page__loading">
          <div class="generate-page__loading-head">
            <span class="memo-chip memo-chip--soft">正在成型</span>
          </div>
          <div class="generate-page__skeleton">
            <span v-for="index in 8" :key="index" class="generate-page__skeleton-line" :style="{ width: `${index % 3 === 0 ? 92 : index % 2 === 0 ? 74 : 86}%` }" />
          </div>
        </div>

        <div v-else-if="result" class="generate-page__result-shell">
          <div class="generate-page__result-head">
            <div>
              <p class="generate-page__section-label">RESULT</p>
              <h3 class="generate-page__result-title">{{ hasAttachment ? attachmentTitle : '本次生成结果' }}</h3>
            </div>
            <div class="generate-page__result-meta">
              <span v-if="hasAttachment && attachmentCountText" class="memo-chip memo-chip--soft">{{ attachmentCountText }}</span>
            </div>
          </div>

          <div class="generate-page__result-content" v-html="renderedResult"></div>
        </div>

        <div v-else class="generate-page__empty">
          <div class="generate-page__empty-hero">
            <p class="generate-page__section-label">READY</p>
            <h3>开始生成你的周报</h3>
            <p>输入本周工作要点，或基于已整理的周记录继续完善内容。</p>
          </div>
        </div>
      </div>
    </section>

    <section class="generate-page__composer-shell">
      <section class="generate-page__composer">
        <div v-if="hasAttachment" class="generate-page__attachment">
          <div class="generate-page__attachment-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="generate-page__attachment-copy">
            <strong>{{ attachmentTitle }}</strong>
            <span>{{ attachmentCountText }}</span>
          </div>
          <button class="generate-page__attachment-remove" type="button" @click="clearAttachment" aria-label="移除已载入素材">
            <el-icon><Close /></el-icon>
          </button>
        </div>

        <textarea
          v-model="promptText"
          class="generate-page__textarea"
          :placeholder="hasAttachment ? '补充要求、增强词或改写方向，例如：请改成更适合周会汇报的表达。' : '输入工作流水、补充要求或增强词...'"
        />

        <div class="generate-page__composer-footer">
          <div class="generate-page__composer-left">
            <StyleSelector v-model="style" compact />

            <button class="generate-page__config-toggle" type="button" @click="configExpanded = !configExpanded">
              <el-icon><Setting /></el-icon>
              <span>{{ configExpanded ? '收起说明' : '风格说明' }}</span>
            </button>
          </div>

          <AppButton
            type="primary"
            variant="primary"
            :loading="generating"
            :disabled="generating || !canGenerate"
            @click="handleGenerate"
          >
            {{ result ? '重新生成' : '生成周报' }}
          </AppButton>
        </div>

        <div v-if="configExpanded" class="generate-page__config-panel">
          <div class="generate-page__config-item">
            <span class="memo-chip memo-chip--accent">{{ currentStyleLabel }}</span>
            <p>{{ styleDescription }}</p>
          </div>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import html2pdf from 'html2pdf.js'
import { ElMessage } from 'element-plus'
import { Close, Document, Setting } from '@element-plus/icons-vue'
import AppButton from '@/components/ui/AppButton.vue'
import StyleSelector from '@/components/StyleSelector.vue'
import { getStyleLabel, normalizeStyle } from '@/components/common/themeConfig'
import { summaryService } from '@/services/summary.service'

const route = useRoute()

const promptText = ref('')
const style = ref('list')
const generating = ref(false)
const result = ref('')
const configExpanded = ref(false)
const attachment = ref(null)

const renderedResult = computed(() => (result.value ? marked.parse(result.value) : ''))
const hasAttachment = computed(() => Boolean(attachment.value?.sourceText))
const attachmentTitle = computed(() => attachment.value?.weekTitle || attachment.value?.title || '已载入周记录')
const attachmentCountText = computed(() => {
  const count = Number(attachment.value?.fragmentCount || 0)
  return count > 0 ? `${count} 条碎片` : '已载入周记录素材'
})
const currentStyleLabel = computed(() => getStyleLabel(style.value))
const canGenerate = computed(() => Boolean(promptText.value.trim() || hasAttachment.value))

const statusText = computed(() => {
  if (generating.value) return '生成中'
  if (result.value) return '已生成'
  return '未生成'
})

const statusChipClass = computed(() => {
  if (generating.value) return 'memo-chip--accent'
  if (result.value) return 'memo-chip--success'
  return 'memo-chip--soft'
})

const styleDescription = computed(() => {
  if (normalizeStyle(style.value) === 'table') {
    return '表格风格会优先把进展、结果、问题和计划组织成 Markdown 表格，更适合结构化汇报。'
  }
  return '列表风格会优先输出标题与分点列表，更适合直接阅读、复制或继续改写。'
})

const loadGenerateContext = () => {
  if (route.query.source !== 'memo-week') return
  try {
    const raw = localStorage.getItem('smart-summary:generate-result')
    if (!raw) return
    const payload = JSON.parse(raw)
    attachment.value = payload
    result.value = payload.summary || ''
  } catch {
    attachment.value = null
  }
}

const buildRequestText = () => {
  const prompt = promptText.value.trim()
  if (!hasAttachment.value) return prompt

  const parts = [attachment.value.sourceText]
  if (prompt) {
    parts.push('', `补充要求：${prompt}`)
  }
  return parts.join('\n')
}

const handleGenerate = async () => {
  const requestText = buildRequestText()
  if (!requestText.trim()) {
    ElMessage.warning('请输入工作记录或补充要求')
    return
  }

  generating.value = true
  try {
    const { data } = await summaryService.generate({ text: requestText, style: style.value })
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
  temp.innerHTML = renderedResult.value
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

const clearAttachment = () => {
  attachment.value = null
  if (route.query.source === 'memo-week') {
    localStorage.removeItem('smart-summary:generate-result')
  }
}

onMounted(() => {
  loadGenerateContext()
})
</script>

<style scoped>
.generate-page {
  gap: var(--app-space-4);
  flex: 1;
  min-height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  overflow: hidden;
}

.generate-page__topbar,
.generate-page__composer {
  border-radius: var(--app-radius-2xl);
  border: 1px solid var(--memo-border);
  background: rgba(255, 255, 255, 0.86);
}

.generate-page__topbar {
  width: min(880px, 100%);
  margin-inline: auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  box-shadow: 0 12px 28px rgba(39, 72, 124, 0.05);
}

.generate-page__topbar-copy {
  min-width: 0;
}

.generate-page__topbar-copy :deep(.app-title) {
  font-size: 20px;
}

.generate-page__topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.generate-page__section-label {
  margin: 0 0 6px;
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.generate-page__stage {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  background: transparent;
}

.generate-page__stage-scroll {
  flex: 1 1 0;
  min-height: 0;
  height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  padding: 8px 8px 0;
}

.generate-page__loading,
.generate-page__result-shell,
.generate-page__empty {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.generate-page__result-shell {
  min-height: auto;
}

.generate-page__loading {
  gap: 18px;
}

.generate-page__loading-head,
.generate-page__result-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.generate-page__skeleton {
  display: grid;
  gap: 14px;
  padding: 20px 0 6px;
}

.generate-page__skeleton-line {
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(230, 238, 248, 0.9), rgba(244, 248, 255, 1), rgba(230, 238, 248, 0.9));
  background-size: 200% 100%;
  animation: generate-pulse 1.5s linear infinite;
}

.generate-page__result-shell {
  gap: 18px;
}

.generate-page__result-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(84, 112, 161, 0.1);
}

.generate-page__result-title {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.generate-page__result-content {
  line-height: 1.9;
  color: var(--app-color-text);
}

.generate-page__result-content :deep(h1) {
  font-size: 24px;
  margin: 0 0 14px;
  letter-spacing: -0.02em;
}

.generate-page__result-content :deep(h2) {
  font-size: 19px;
  margin: 22px 0 10px;
}

.generate-page__result-content :deep(h3) {
  font-size: 16px;
  margin: 18px 0 8px;
}

.generate-page__result-content :deep(p),
.generate-page__result-content :deep(li) {
  line-height: 1.85;
}

.generate-page__result-content :deep(ul),
.generate-page__result-content :deep(ol) {
  padding-left: 1.4em;
}

.generate-page__result-content :deep(blockquote) {
  margin: 14px 0;
  padding: 12px 14px;
  border-left: 3px solid rgba(59, 130, 246, 0.28);
  border-radius: 0 14px 14px 0;
  background: rgba(243, 248, 255, 0.9);
  color: var(--app-color-text-soft);
}

.generate-page__result-content :deep(code) {
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(236, 243, 255, 0.96);
  color: var(--app-color-text-strong);
  font-size: 0.92em;
}

.generate-page__result-content :deep(pre) {
  overflow-x: auto;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(245, 249, 255, 0.96);
  border: 1px solid rgba(84, 112, 161, 0.1);
}

.generate-page__result-content :deep(pre code) {
  padding: 0;
  background: transparent;
}

.generate-page__result-content :deep(table) {
  width: max-content;
  min-width: 100%;
  border-collapse: collapse;
  margin: 14px 0 8px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 26px rgba(39, 72, 124, 0.06);
}

.generate-page__result-content :deep(th),
.generate-page__result-content :deep(td) {
  border: 1px solid rgba(84, 112, 161, 0.14);
  padding: 11px 13px;
  text-align: left;
  vertical-align: top;
  white-space: nowrap;
}

.generate-page__result-content :deep(th) {
  background: linear-gradient(180deg, rgba(233, 242, 255, 0.95), rgba(226, 237, 255, 0.88));
  color: var(--app-color-text-strong);
  font-weight: 700;
}

.generate-page__result-content :deep(tr:nth-child(even) td) {
  background: rgba(248, 251, 255, 0.72);
}

.generate-page__empty {
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-align: center;
  padding: 12px 24px 0;
}

.generate-page__empty-hero {
  max-width: 540px;
}

.generate-page__empty-hero h3 {
  margin: 0 0 10px;
  font-size: 28px;
  color: var(--app-color-text-strong);
}

.generate-page__empty-hero p {
  margin: 0;
  color: var(--app-color-text-soft);
  line-height: 1.8;
}

.generate-page__composer-shell {
  flex: none;
  display: flex;
  justify-content: center;
  padding-top: 4px;
}

.generate-page__composer {
  width: min(900px, 100%);
  padding: 10px 12px 10px;
  border-radius: 28px;
  box-shadow: 0 18px 38px rgba(39, 72, 124, 0.08);
}

.generate-page__attachment {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  margin-bottom: 12px;
  border-radius: 18px;
  border: 1px solid rgba(59, 130, 246, 0.14);
  background: linear-gradient(180deg, rgba(243, 248, 255, 0.96), rgba(236, 244, 255, 0.92));
}

.generate-page__attachment-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2563eb, #60a5fa);
  color: #fff;
  font-size: 20px;
  box-shadow: 0 10px 18px rgba(37, 99, 235, 0.18);
}

.generate-page__attachment-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.generate-page__attachment-copy strong {
  color: var(--app-color-text-strong);
  font-size: 15px;
}

.generate-page__attachment-copy span {
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.generate-page__attachment-remove {
  margin-left: auto;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.86);
  color: var(--app-color-text-muted);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.generate-page__attachment-remove:hover {
  background: rgba(255, 255, 255, 1);
  color: var(--app-color-text);
}

.generate-page__textarea {
  width: 100%;
  min-height: 82px;
  resize: none;
  padding: 12px 14px;
  border-radius: 18px;
  border: 0;
  background: transparent;
  color: var(--app-color-text);
  outline: none;
  line-height: 1.7;
  font-size: 15px;
}

.generate-page__textarea:focus {
  box-shadow: none;
}

.generate-page__composer-footer {
  margin-top: 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.generate-page__composer-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.generate-page__config-toggle {
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(84, 112, 161, 0.12);
  background: rgba(247, 250, 255, 0.92);
  color: var(--app-color-text-muted);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.generate-page__config-toggle:hover {
  color: var(--app-color-text);
  background: rgba(255, 255, 255, 1);
}

.generate-page__config-panel {
  margin-top: 10px;
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid rgba(84, 112, 161, 0.1);
  background: rgba(247, 250, 255, 0.9);
}

.generate-page__config-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  flex-wrap: wrap;
}

.generate-page__config-item p {
  margin: 2px 0 0;
  color: var(--app-color-text-soft);
  line-height: 1.7;
  font-size: 13px;
}

@keyframes generate-pulse {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 960px) {
  .generate-page__topbar,
  .generate-page__composer-footer {
    align-items: stretch;
  }

  .generate-page__topbar {
    flex-direction: column;
  }

  .generate-page__topbar-actions {
    justify-content: flex-start;
  }

  .generate-page__composer {
    width: 100%;
  }
}
</style>
