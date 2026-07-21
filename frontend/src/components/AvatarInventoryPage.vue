<template>
  <div class="avatar-page">
    <header class="top-bar">
      <button class="back-btn" @click="$router.back()" aria-label="Back">
        <span class="material-symbols-outlined">arrow_back_ios_new</span>
      </button>
      <h2>My Avatars</h2>
      <div class="spacer"></div>
    </header>

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat koleksi avatar..." />

      <template v-else>
        <p class="hint-text">
          Avatar yang kamu beli di Shop muncul di sini. Tap salah satu untuk memakainya
          sebagai foto profil di dalam app.
        </p>

        <section class="avatar-grid">
          <button class="avatar-slot" :class="{ active: usingDefault }" @click="handleReset">
            <img :src="defaultAvatarUrl" alt="Foto profil Telegram" />
            <span class="slot-label">Default (Telegram)</span>
            <span v-if="usingDefault" class="check-badge material-symbols-outlined">check_circle</span>
          </button>

          <button
            v-for="avatar in avatars"
            :key="avatar.id"
            class="avatar-slot"
            :class="{ active: avatar.equipped }"
            :disabled="equippingId === avatar.id"
            @click="handleEquip(avatar)"
          >
            <img :src="avatar.assetUrl" :alt="avatar.title" />
            <span class="slot-label">{{ avatar.title }}</span>
            <span v-if="avatar.equipped" class="check-badge material-symbols-outlined">check_circle</span>
          </button>
        </section>

        <p v-if="avatars.length === 0" class="empty-text">
          Kamu belum punya avatar limited. Beli di
          <router-link to="/shop">Shop</router-link> kategori "Cosmetics".
        </p>
      </template>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { cachedApiGet, invalidate } from '../lib/api'
import LoadingSpinner from './LoadingSpinner.vue'

const loading = ref(true)
const defaultAvatarUrl = ref('')
const usingDefault = ref(true)
const avatars = ref([])
const equippingId = ref(null)

async function loadAvatars() {
  loading.value = true
  try {
    const data = await cachedApiGet('/inventory/avatars', { ttl: 60 * 1000 })
    defaultAvatarUrl.value = data.defaultAvatarUrl
    usingDefault.value = data.usingDefault
    avatars.value = data.avatars
  } catch (err) {
    console.error('Failed to load avatar inventory', err)
  } finally {
    loading.value = false
  }
}

// Setelah equip/reset berhasil, avatar yang tampil di header & profil
// berubah, jadi cache dashboard/profile ikut di-invalidate supaya
// langsung sinkron begitu user balik ke halaman itu.
function invalidateProfileCaches() {
  invalidate('/inventory/avatars')
  invalidate('/profile/me')
  invalidate('/dashboard/summary')
}

async function handleEquip(avatar) {
  if (equippingId.value) return
  equippingId.value = avatar.id
  try {
    await api.post(`/inventory/avatars/${avatar.id}/equip`)
    invalidateProfileCaches()
    await loadAvatars()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal memakai avatar ini')
  } finally {
    equippingId.value = null
  }
}

async function handleReset() {
  if (usingDefault.value || equippingId.value) return
  equippingId.value = 'default'
  try {
    await api.post('/inventory/avatars/reset')
    invalidateProfileCaches()
    await loadAvatars()
  } catch (err) {
    console.error('Failed to reset avatar', err)
  } finally {
    equippingId.value = null
  }
}

onMounted(loadAvatars)
</script>

<style scoped>
.avatar-page { min-height: 100dvh; background: #0d1226; color: #dce1fc; }
.top-bar {
  position: fixed; top: 0; left: 0; width: 100%; z-index: 50;
  background: rgba(13, 18, 38, 0.8); backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; justify-content: space-between;
  height: 64px; padding: 0 12px;
}
.back-btn {
  width: 40px; height: 40px; border-radius: 50%; background: none; border: none;
  color: #b5c4ff; display: flex; align-items: center; justify-content: center; cursor: pointer;
}
.back-btn:hover { background: rgba(255, 255, 255, 0.05); }
.top-bar h2 { font-size: 16px; font-weight: 700; margin: 0; }
.spacer { width: 40px; }
.content {
  max-width: 480px; margin: 0 auto; padding: 96px 20px 48px;
  display: flex; flex-direction: column; gap: 20px;
}
.hint-text { font-size: 12px; color: rgba(195, 197, 215, 0.7); line-height: 1.5; margin: 0; }
.avatar-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.avatar-slot {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
}
.avatar-slot.active { border-color: #b5c4ff; box-shadow: 0 0 12px rgba(79, 125, 255, 0.3); }
.avatar-slot:disabled { opacity: 0.5; cursor: wait; }
.avatar-slot img {
  width: 56px; height: 56px; border-radius: 50%; object-fit: cover; background: #191f32;
}
.slot-label {
  font-size: 10px; font-weight: 700; text-align: center; color: #c3c5d7;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%;
}
.check-badge {
  position: absolute; top: 4px; right: 4px; font-size: 16px; color: #34d399;
  font-variation-settings: 'FILL' 1;
}
.empty-text { text-align: center; font-size: 13px; color: rgba(195, 197, 215, 0.6); }
.empty-text a { color: #b5c4ff; }
</style>
