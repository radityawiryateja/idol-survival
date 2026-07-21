<template>
  <div class="admin-page">
    <header class="top-bar">
      <h2>Admin Panel</h2>
    </header>

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat data admin..." />

      <template v-else>
        <section class="stat-grid">
          <div class="stat-card">
            <span class="stat-label">TOTAL PRODUCERS</span>
            <span class="stat-value">{{ overview.totalProducers }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">TOTAL IDOLS</span>
            <span class="stat-value">{{ overview.totalIdols }}</span>
          </div>
        </section>

        <p class="hint-text">
          Panel ini contoh dasar — kembangkan sesuai kebutuhan (manajemen idol,
          moderasi Talks, atur role producer via <code>PATCH /admin/producers/:id/role</code>).
        </p>
      </template>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { cachedApiGet } from '../lib/api'
import LoadingSpinner from './LoadingSpinner.vue'

const loading = ref(true)
const overview = ref({ totalProducers: 0, totalIdols: 0 })

async function loadOverview() {
  loading.value = true
  try {
    overview.value = await cachedApiGet('/admin/overview', { ttl: 30 * 1000 })
  } catch (err) {
    console.error('Failed to load admin overview', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadOverview)
</script>

<style scoped>
.admin-page { min-height: 100dvh; background: #0d1226; color: #dce1fc; }
.top-bar {
  position: fixed; top: 0; left: 0; width: 100%; z-index: 50;
  background: rgba(13, 18, 38, 0.8); backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; height: 64px; padding: 0 20px;
}
.top-bar h2 { font-size: 16px; font-weight: 700; margin: 0; }
.content {
  max-width: 480px; margin: 0 auto; padding: 96px 20px 48px;
  display: flex; flex-direction: column; gap: 20px;
}
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.stat-card {
  border-radius: 16px; padding: 20px;
  background: rgba(20, 28, 52, 0.8); border: 1px solid rgba(255,255,255,0.1);
  display: flex; flex-direction: column; gap: 4px;
}
.stat-label { font-size: 11px; font-weight: 700; letter-spacing: 0.05em; color: #c3c5d7; }
.stat-value { font-size: 24px; font-weight: 700; color: #b5c4ff; }
.hint-text { font-size: 12px; color: rgba(195,197,215,0.6); line-height: 1.6; }
.hint-text code { color: #b5c4ff; }
</style>
