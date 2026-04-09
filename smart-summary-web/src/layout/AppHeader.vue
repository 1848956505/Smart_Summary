<template>
  <header class="app-header">
    <div class="app-header__left">
      <AppBreadcrumb :items="breadcrumb" />
      <h1 class="app-header__title">{{ title }}</h1>
    </div>
    <div class="app-header__right">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup>
import AppBreadcrumb from './AppBreadcrumb.vue'

defineProps({
  title: { type: String, default: '' },
  breadcrumb: { type: Array, default: () => [] }
})
</script>

<style scoped>
.app-header {
  min-height: var(--app-header-height);
  padding: 0 var(--app-space-6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--app-space-4);
  border-bottom: 1px solid var(--app-panel-border);
  background: var(--app-navbar-bg);
  flex-shrink: 0;
}

.app-header__left {
  min-width: 0;
}

.app-header__title {
  margin: 4px 0 0;
  font-size: 20px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.app-header__right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
</style>
