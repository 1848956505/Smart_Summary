<template>
  <main class="app-content" :class="{ 'app-content--full-bleed': props.fullBleed }">
    <div :class="contentFrameClass">
      <slot />
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  contentWidth: {
    type: String,
    default: 'standard'
  },
  fullBleed: {
    type: Boolean,
    default: false
  }
})

const contentFrameClass = computed(() => [
  'app-content__frame',
  props.fullBleed ? 'app-content__frame--full-bleed' : `app-page-width--${props.contentWidth || 'standard'}`
])
</script>

<style scoped>
.app-content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  height: 100%;
  overflow: hidden;
  background: transparent;
}

.app-content__frame {
  width: 100%;
  min-height: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding-block: var(--app-space-5);
  padding-inline: var(--app-space-4);
  box-sizing: border-box;
}

.app-content__frame--full-bleed {
  padding-inline: calc(var(--app-shell-gutter) + var(--app-space-2));
  max-width: none;
}
</style>
