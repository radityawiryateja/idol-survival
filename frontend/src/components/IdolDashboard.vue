<template>
  <div class="idol-panel-page">
    <header class="top-bar">
      <h2>Idol Panel</h2>
    </header>

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat profil idol..." />

      <template v-else-if="idol">
        <section class="profile-card">
          <img :src="idol.photo_url" :alt="idol.name" class="idol-photo" />
          <div>
            <h3>{{ idol.name }}</h3>
            <p>{{ idol.agency }}</p>
          </div>
        </section>

        <section class="messages-section">
          <h3>Pesan Fans Terbaru</h3>
          <div v-for="msg in messages" :key="msg.id" class="message-row">
            <span class="message-sender">{{ msg.sender === 'user' ? 'Fan' : 'Kamu' }}</span>
            <p>{{ msg.content }}</p>
          </div>
          <p v-if="messages.length === 0" class="empty-text">Belum ada pesan.</p>
        </section>
      </template>

      <p v-else class="empty-text">
        Akun ini belum ditautkan ke profil idol. Hubungi admin untuk penautan.
      </p>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { cachedApiGet } from '../lib/api'
import LoadingSpinner from './LoadingSpinner.vue'

const loading = ref(true)
const idol = ref(null)
const messages = ref([])

async function loadPanel() {
  loading.value = true
  try {
    idol.value = await cachedApiGet('/idol-panel/me', { ttl: 60 * 1000 })
    const data = await cachedApiGet('/idol-panel/messages', { ttl: 30 * 1000 })
    messages.value = data.messages
  } catch (err) {
    idol.value = null
    console.error('Failed to load idol panel', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadPanel)
</script>

<style scoped>
.idol-panel-page { min-height: 100dvh; background: #0d1226; color: #dce1fc; }
.top-bar {
  position: fixed; top: 0; left: 0; width: 100%; z-index: 50;
  background: rgba(13, 18, 38, 0.8); backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; height: 64px; padding: 0 20px;
}
.top-bar h2 { font-size: 16px; font-weight: 700; margin: 0; }
.content {
  max-width: 480px; margin: 0 auto; padding: 96px 20px 48px;
  display: flex; flex-direction: column; gap: 24px;
}
.profile-card { display: flex; align-items: center; gap: 16px; }
.idol-photo { width: 64px; height: 64px; border-radius: 50%; object-fit: cover; }
.profile-card h3 { margin: 0; font-size: 18px; }
.profile-card p { margin: 2px 0 0; font-size: 12px; color: #c3c5d7; }
.messages-section h3 { font-size: 14px; margin: 0 0 12px; color: #c3c5d7; }
.message-row {
  padding: 12px; border-radius: 12px; margin-bottom: 8px;
  background: rgba(20, 28, 52, 0.8); border: 1px solid rgba(255,255,255,0.1);
}
.message-sender { font-size: 10px; font-weight: 700; color: #b5c4ff; }
.message-row p { margin: 4px 0 0; font-size: 13px; }
.empty-text { text-align: center; font-size: 13px; color: rgba(195,197,215,0.6); }
</style>
