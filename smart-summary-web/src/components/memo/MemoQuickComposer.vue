<template>
  <section class="memo-composer app-surface">
    <div class="memo-composer__top">
      <div class="memo-composer__date">
        <span class="memo-composer__date-label">当前录入日期</span>
        <button type="button" class="memo-composer__date-chip" @click="$emit('jump-today')" :title="activeDate">
          <el-icon><Calendar /></el-icon>
          <span>{{ activeDate || '未选择' }}</span>
        </button>
      </div>
    </div>

    <div class="memo-composer__input">
      <textarea
        ref="textareaRef"
        :value="modelValue"
        class="memo-composer__textarea"
        :placeholder="placeholder"
        rows="1"
        @input="handleInput"
        @keydown.enter.exact.prevent="handleSubmit"
        @keydown.enter.shift.stop
      />
      <el-button class="memo-composer__submit" type="primary" :disabled="!trimmedValue" @click="handleSubmit">
        <el-icon><Promotion /></el-icon>
      </el-button>
    </div>

    <div class="memo-composer__footer">
      <span>Enter 保存，Shift+Enter 换行</span>
      <button type="button" class="memo-composer__footer-link" @click="$emit('open-detail')">打开详细录入</button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Calendar, Promotion } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  activeDate: { type: String, default: '' },
  placeholder: {
    type: String,
    default: '记下此刻的工作碎片...'
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'open-detail', 'jump-today'])
const textareaRef = ref(null)

const trimmedValue = computed(() => props.modelValue.trim())

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  autoResize(event.target)
}

const handleSubmit = () => {
  if (!trimmedValue.value) return
  emit('submit', props.modelValue)
}

const autoResize = (el) => {
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

watch(
  () => props.modelValue,
  () => {
    if (textareaRef.value) autoResize(textareaRef.value)
  }
)
</script>

<style scoped>
.memo-composer {
  padding: 16px 18px 14px;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
}

.memo-composer__top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.memo-composer__date {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.memo-composer__date-label {
  font-size: 12px;
  color: var(--app-color-text-muted);
  letter-spacing: 0.06em;
}

.memo-composer__date-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--app-color-primary-soft);
  color: var(--app-color-primary-strong);
  font-size: 12px;
  font-weight: 700;
  border: 0;
}

.memo-composer__input {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 2px 0;
}

.memo-composer__textarea {
  flex: 1;
  min-height: 54px;
  max-height: 180px;
  resize: none;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--app-color-text);
  line-height: 1.7;
  font-size: 15px;
  padding: 10px 2px;
}

.memo-composer__textarea::placeholder {
  color: rgba(148, 163, 184, 0.82);
}

.memo-composer__submit {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.18);
}

.memo-composer__footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid rgba(226, 232, 240, 0.65);
  font-size: 11px;
  color: var(--app-color-text-muted);
}

.memo-composer__footer-link {
  border: 0;
  background: transparent;
  color: var(--app-color-primary);
  font-size: 11px;
  font-weight: 700;
}

@media (max-width: 860px) {
  .memo-composer__input {
    align-items: stretch;
  }

  .memo-composer__submit {
    align-self: flex-end;
  }
}
</style>
