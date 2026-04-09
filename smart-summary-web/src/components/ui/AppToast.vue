<template>
  <transition name="fade">
    <div v-if="visible" class="app-toast" :class="`app-toast--${type}`">
      <slot />
    </div>
  </transition>
</template>

<script setup>
defineProps({
  visible: Boolean,
  type: {
    type: String,
    default: 'info'
  }
})
</script>

<style scoped>
.app-toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 60;
  padding: 12px 16px;
  border-radius: var(--app-radius-md);
  color: #fff;
  box-shadow: var(--app-shadow-lg);
}
.app-toast--success { background: #16a34a; }
.app-toast--error { background: #dc2626; }
.app-toast--info { background: #2563eb; }
</style>
