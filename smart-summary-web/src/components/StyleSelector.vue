<template>
  <div :class="['style-selector', compact && 'style-selector--compact']">
    <div v-if="!compact" class="style-selector__label">{{ label }}</div>

    <div :class="['app-segmented', compact && 'app-segmented--compact']">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        :class="['app-segmented__option', { 'is-active': modelValue === option.value }]"
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
    default: 'list'
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

.style-selector__icon {
  font-size: 16px;
}

.style-selector--compact {
  gap: 8px;
}
</style>
