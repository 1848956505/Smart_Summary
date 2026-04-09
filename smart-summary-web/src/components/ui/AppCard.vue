<template>
  <section :class="['app-card', compact && 'app-card--compact']">
    <header v-if="$slots.header" class="app-card__header">
      <slot name="header" />
    </header>
    <div class="app-card__body">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  compact: {
    type: Boolean,
    default: false
  }
})
</script>
