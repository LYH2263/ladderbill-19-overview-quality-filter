<script setup>
import { quality, QUALITY_OPTIONS } from '../stores/qualityFilter'
</script>

<template>
  <div class="quality-filter">
    <span class="muted">质量过滤</span>
    <button
      v-for="opt in QUALITY_OPTIONS"
      :key="opt.value"
      type="button"
      :class="{ active: quality === opt.value }"
      @click="quality = opt.value"
    >{{ opt.label }}</button>
  </div>
</template>

<style scoped>
.quality-filter { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
button {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--muted);
  padding: 0.3rem 0.8rem;
}
button.active { background: var(--accent); border-color: var(--accent); color: #111; }
</style>
