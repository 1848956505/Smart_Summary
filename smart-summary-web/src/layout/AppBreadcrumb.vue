<template>
  <nav class="app-breadcrumb">
    <template v-for="(item, index) in items" :key="item.label">
      <router-link v-if="item.to" :to="item.to" class="app-breadcrumb__item">{{ item.label }}</router-link>
      <span v-else class="app-breadcrumb__item">{{ item.label }}</span>
      <span v-if="index < items.length - 1" class="app-breadcrumb__sep">/</span>
    </template>
  </nav>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.app-breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--app-color-text-muted);
}

.app-breadcrumb__item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.app-breadcrumb__sep {
  color: var(--app-color-border-strong);
}
</style>
