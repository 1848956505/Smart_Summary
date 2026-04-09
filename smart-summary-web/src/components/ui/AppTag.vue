<template>
  <el-tag :type="type" :effect="effect" class="app-tag"><slot /></el-tag>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'info'
  },
  effect: {
    type: String,
    default: 'light'
  }
})
</script>

<style scoped>
.app-tag {
  border-radius: 999px;
  font-weight: 600;
}
</style>
