<template>
  <section class="memo-composer app-surface">
    <div class="memo-composer__context">
      <div class="memo-composer__date">
        <span class="memo-composer__date-label">当前录入日期</span>
        <button type="button" class="memo-chip memo-chip--content memo-composer__date-chip" :title="activeDate" @click="$emit('jump-today')">
          <el-icon><Calendar /></el-icon>
          <span>{{ activeDate || '未选择' }}</span>
        </button>
      </div>

      <button type="button" class="memo-button memo-button--ghost memo-composer__detail-link" @click="$emit('open-detail')">打开详细录入</button>
    </div>

    <div class="memo-composer__field">
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

      <button class="memo-button memo-button--primary memo-button--icon memo-composer__submit" type="button" :disabled="!trimmedValue" @click="handleSubmit">
        <el-icon><Promotion /></el-icon>
      </button>
    </div>

    <div class="memo-composer__meta">
      <span>回车保存，Shift + 回车换行</span>
      <span>随手记下这一刻的工作碎片</span>
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
  padding: 14px 18px;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid var(--memo-border);
  backdrop-filter: blur(16px);
  box-shadow: var(--memo-shadow-soft);
}

.memo-composer:focus-within {
  border-color: var(--memo-border-strong);
  box-shadow: var(--memo-selected-shadow);
}

.memo-composer__context {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.memo-composer__date {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.memo-composer__date-label {
  font-size: 12px;
  color: var(--app-color-text-muted);
  letter-spacing: 0.04em;
}

.memo-composer__date-chip {
  gap: 6px;
}

.memo-composer__detail-link {
  min-width: 112px;
}

.memo-composer__field {
  display: flex;
  align-items: flex-end;
  gap: 10px;
}

.memo-composer__textarea {
  flex: 1;
  min-height: 52px;
  max-height: 180px;
  resize: none;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--app-color-text);
  line-height: 1.8;
  font-size: 15px;
  padding: 8px 2px;
}

.memo-composer__textarea::placeholder {
  color: rgba(148, 163, 184, 0.82);
}

.memo-composer__submit {
  box-shadow: var(--memo-button-primary-shadow);
}

.memo-composer__meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid var(--memo-line-soft);
  font-size: 11px;
  color: var(--app-color-text-muted);
  flex-wrap: wrap;
}

@media (max-width: 860px) {
  .memo-composer__field {
    align-items: stretch;
  }

  .memo-composer__submit {
    align-self: flex-end;
  }

  .memo-composer__meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

