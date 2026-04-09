<template>
  <div class="app-loading">
    <el-skeleton :rows="rows" animated />
  </div>
</template>

<script setup>
defineProps({
  rows: {
    type: Number,
    default: 3
  }
})
</script>

<style scoped>
.app-loading {
  padding: var(--app-space-6);
}
</style>
