<template>
  <div class="loading-wrap">
    <div class="loading-spinner"></div>
    <p v-if="label" class="loading-label">{{ label }}</p>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: '' },
})
</script>

<style scoped>
.loading-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 64px 0;
  width: 100%;
}
.loading-spinner {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 3px solid rgba(181, 196, 255, 0.15);
  border-top-color: #b5c4ff;
  animation: spin 0.8s linear infinite;
}
.loading-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: rgba(195, 197, 215, 0.6);
  margin: 0;
  text-transform: uppercase;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
