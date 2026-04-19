<template>
  <div :class="['style-selector', compact && 'style-selector--compact']">
    <div v-if="!compact" class="style-selector__label">{{ label }}</div>

    <div class="style-selector__rail">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        :class="['style-selector__chip', { active: modelValue === option.value }]"
        @click="handleClick(option.value)"
      >
        <el-icon v-if="option.icon" class="style-selector__icon">
          <component :is="option.icon" />
        </el-icon>
        <span>{{ option.label }}</span>
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
    default: '风格'
  },
  compact: {
    type: Boolean,
    default: false
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
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.style-selector__label {
  color: var(--app-color-text-muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.style-selector__rail {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid rgba(226, 232, 240, 0.92);
}

.style-selector__chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--app-color-text-muted);
  font-weight: 700;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
  white-space: nowrap;
}

.style-selector__chip:hover:not(.active) {
  background: rgba(255, 255, 255, 0.95);
  color: var(--app-color-text);
  transform: translateY(-1px);
}

.style-selector__chip.active {
  background: rgba(37, 99, 235, 0.08);
  color: var(--app-color-primary);
}

.style-selector__icon {
  font-size: 16px;
}

.style-selector--compact {
  gap: 8px;
}

.style-selector--compact .style-selector__rail {
  padding: 4px;
}

.style-selector--compact .style-selector__chip {
  padding: 7px 10px;
  font-size: 12px;
}
</style>
