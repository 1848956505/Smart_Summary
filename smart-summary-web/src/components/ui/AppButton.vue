<template>
  <el-button :class="buttonClass" v-bind="$attrs" :type="type" :size="size" :loading="loading" :disabled="disabled">
    <slot />
  </el-button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'default'
  },
  size: {
    type: String,
    default: 'default'
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'default'
  }
})

const resolvedVariant = computed(() => {
  if (props.variant && props.variant !== 'default') return props.variant
  if (props.type === 'primary') return 'primary'
  if (props.type === 'danger') return 'danger'
  return 'default'
})

const buttonClass = computed(() => ['app-button', `app-button--${resolvedVariant.value}`])
</script>

<style scoped>
.app-button {
  --app-button-bg: var(--app-surface-elevated-max);
  --app-button-border: var(--app-border-default);
  --app-button-text: var(--app-color-text);
  --app-button-shadow: none;
  --app-button-hover-bg: var(--app-surface-hover);
  --app-button-hover-border: var(--app-accent-border);
  --app-button-hover-text: var(--app-color-primary-strong);
  --app-button-hover-shadow: var(--app-elevation-interactive);
  --app-button-active-shadow: var(--app-elevation-interactive);
  border: 1px solid var(--app-button-border);
  border-radius: var(--app-radius-md);
  background: var(--app-button-bg);
  color: var(--app-button-text);
  font-weight: 600;
  box-shadow: var(--app-button-shadow);
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.app-button:hover,
.app-button:focus-visible {
  background: var(--app-button-hover-bg);
  border-color: var(--app-button-hover-border);
  color: var(--app-button-hover-text);
  box-shadow: var(--app-button-hover-shadow);
  transform: translateY(-1px);
}

.app-button:active {
  box-shadow: var(--app-button-active-shadow);
  transform: translateY(0);
}

.app-button.is-disabled,
.app-button.is-disabled:hover {
  transform: none;
  box-shadow: none;
}

.app-button--primary {
  --app-button-bg: var(--app-gradient-primary);
  --app-button-border: color-mix(in srgb, var(--app-color-primary) 34%, transparent);
  --app-button-text: #ffffff;
  --app-button-shadow: var(--app-elevation-primary);
  --app-button-hover-bg: var(--app-gradient-primary-hover);
  --app-button-hover-border: color-mix(in srgb, var(--app-color-primary-strong) 42%, transparent);
  --app-button-hover-text: #ffffff;
  --app-button-hover-shadow: var(--app-elevation-primary);
}

.app-button--ghost {
  --app-button-bg: transparent;
  --app-button-border: transparent;
  --app-button-text: var(--app-color-text-soft);
  --app-button-hover-bg: var(--app-surface-soft);
  --app-button-hover-border: var(--app-border-default);
  --app-button-hover-text: var(--app-color-text);
}

.app-button--danger {
  --app-button-bg: color-mix(in srgb, var(--app-color-danger) 8%, var(--app-surface-elevated-max));
  --app-button-border: color-mix(in srgb, var(--app-color-danger) 24%, transparent);
  --app-button-text: var(--app-color-danger);
  --app-button-hover-bg: color-mix(in srgb, var(--app-color-danger) 12%, var(--app-surface-elevated-max));
  --app-button-hover-border: color-mix(in srgb, var(--app-color-danger) 32%, transparent);
  --app-button-hover-text: var(--app-color-danger);
}

.app-button--link {
  --app-button-bg: transparent;
  --app-button-border: transparent;
  --app-button-text: var(--app-color-primary);
  --app-button-shadow: none;
  --app-button-hover-bg: transparent;
  --app-button-hover-border: transparent;
  --app-button-hover-text: var(--app-color-primary-strong);
  --app-button-hover-shadow: none;
  padding-inline: 0;
}
</style>
