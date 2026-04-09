<template>
  <main class="app-content">
    <slot />
  </main>
</template>

<style scoped>
.app-content {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: var(--app-space-6);
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.72), rgba(241, 245, 249, 0.88));
}
</style>
