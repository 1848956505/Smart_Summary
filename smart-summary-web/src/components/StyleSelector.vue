<template>
  <div class="style-selector">
    <label class="style-selector__label">{{ label }}</label>
    <div class="style-selector__container">
      <button
        v-for="option in options"
        :key="option.value"
        :class="['style-selector__btn', { active: modelValue === option.value }]"
        @click="handleClick(option.value)"
      >
        <el-icon class="style-selector__icon">
          <component :is="option.icon" />
        </el-icon>
        <span class="style-selector__text">{{ option.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { styleOptions } from '@/components/common/themeConfig'

defineProps({
  modelValue: {
    type: String,
    default: 'dingtalk'
  },
  label: {
    type: String,
    default: 'SELECT STYLE / 选择汇报风格'
  }
})

const emit = defineEmits(['update:modelValue'])
const options = styleOptions

const handleClick = (value) => {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.style-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.style-selector__label {
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.style-selector__container {
  display: inline-flex;
  gap: 6px;
  padding: 6px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 18px;
}

.style-selector__btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 14px;
  background: transparent;
  color: #64748b;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 700;
}

.style-selector__btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.72);
  color: #0f172a;
}

.style-selector__btn.active {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.14), rgba(99, 102, 241, 0.1));
  color: #1d4ed8;
  box-shadow: inset 0 0 0 1px rgba(37, 99, 235, 0.12);
}

.style-selector__icon {
  font-size: 16px;
}
</style>
