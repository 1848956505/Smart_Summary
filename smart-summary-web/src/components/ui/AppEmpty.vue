<template>
  <div class="app-empty">
    <el-empty :description="description" :image-size="imageSize">
      <slot />
    </el-empty>
  </div>
</template>

<script setup>
defineProps({
  description: {
    type: String,
    default: '暂无内容'
  },
  imageSize: {
    type: Number,
    default: 92
  }
})
</script>

<style scoped>
.app-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--app-space-10) var(--app-space-6);
}
</style>
