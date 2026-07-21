<template>
  <div class="settings-page">
    <header class="top-bar">
      <button class="back-btn" @click="$router.back()" aria-label="Back">
        <span class="material-symbols-outlined">arrow_back_ios_new</span>
      </button>
      <h2>Account Settings</h2>
      <div class="spacer"></div>
    </header>

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat pengaturan..." />

      <template v-else>
        <section class="avatar-section">
          <img :src="form.avatarUrl" class="avatar" />
          <p class="telegram-handle" v-if="form.telegramUsername">@{{ form.telegramUsername }}</p>
        </section>

        <!-- 🟢 TAMBAHKAN KODE INVENTORY DI SINI 🟢 -->
        <section class="inventory-section" v-if="myAvatars.length > 0">
          <h3 class="field-label">MY AVATARS</h3>
          <div class="avatar-list">
            <div 
              v-for="avatar in myAvatars" 
              :key="avatar.id"
              class="avatar-item" 
              @click="equipAvatar(avatar.id)"
            >
              <img :src="avatar.assetUrl" class="avatar-preview" :class="{ 'is-equipped': avatar.equipped }" />
              <span v-if="avatar.equipped" class="equipped-badge">Dipakai</span>
            </div>
          </div>
        </section>

        <label class="field">
          <span class="field-label">DISPLAY NAME</span>
          <input v-model="form.displayName" type="text" maxlength="50" class="field-input" />
        </label>

        <label class="field">
          <span class="field-label">BIO</span>
          <textarea v-model="form.bio" maxlength="200" rows="3" class="field-input textarea"></textarea>
          <span class="char-count">{{ form.bio.length }}/200</span>
        </label>

        <p class="info-text">
          Nama & foto profil asli tersinkron otomatis dari akun Telegram kamu
          setiap login. Display name di sini cuma dipakai buat tampilan di app.
        </p>

        <button class="save-btn" :disabled="saving" @click="handleSave">
          {{ saving ? 'Menyimpan...' : 'Simpan Perubahan' }}
        </button>
        <p v-if="savedMessage" class="saved-text">{{ savedMessage }}</p>
      </template>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../lib/api'
import LoadingSpinner from './LoadingSpinner.vue'

const loading = ref(true)
const saving = ref(false)
const savedMessage = ref('')
const myAvatars = ref([])
const form = ref({ displayName: '', bio: '', avatarUrl: '', telegramUsername: '' })

async function loadAccount() {
  loading.value = true
  try {
    const { data } = await api.get('/settings/account')
    form.value = data
  } catch (err) {
    console.error('Failed to load account settings', err)
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  savedMessage.value = ''
  try {
    await api.patch('/settings/account', { displayName: form.value.displayName, bio: form.value.bio })
    savedMessage.value = 'Tersimpan!'
    setTimeout(() => (savedMessage.value = ''), 2000)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menyimpan')
  } finally {
    saving.value = false
  }
}

async function loadInventory() {
  try {
    const { data } = await api.get('/inventory/avatars')
    myAvatars.value = data.avatars
  } catch (err) {
    console.error('Failed to load inventory', err)
  }
}

// Fungsi untuk memakai item
async function equipAvatar(itemId) {
  try {
    await api.post(`/inventory/avatars/${itemId}/equip`)
    await loadAccount() // Tarik ulang data setelah sukses dipakai
    alert("Avatar berhasil diganti!")
  } catch (err) {
    alert("Gagal mengganti avatar")
  }
}

onMounted(() => {
  loadAccount()
  loadInventory()
})
</script>

<style scoped>
.settings-page { min-height: 100dvh; background: #0d1226; color: #dce1fc; }
/* Styling tambahan untuk Inventory Avatar */
.inventory-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 10px 0;
}
.avatar-list {
  display: flex;
  gap: 16px;
  overflow-x: auto; /* Biar bisa di-scroll ke samping kalau avatarnya banyak */
  padding-bottom: 10px;
}
.avatar-item {
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.2s;
}
.avatar-item:hover {
  transform: scale(1.05);
}
.avatar-preview {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.1);
}
.avatar-preview.is-equipped {
  border-color: #34d399; /* Warna hijau penanda lagi dipakai */
}
.equipped-badge {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  background: #34d399;
  color: #0d1226;
  font-size: 9px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 8px;
  white-space: nowrap;
}
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
.avatar-section { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(181,196,255,0.4); }
.telegram-handle { font-size: 12px; color: #c3c5d7; margin: 0; }
.field { display: flex; flex-direction: column; gap: 6px; position: relative; }
.field-label { font-size: 11px; font-weight: 700; letter-spacing: 0.05em; color: #c3c5d7; }
.field-input {
  background: rgba(20, 28, 52, 0.8); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; padding: 12px 16px; color: #dce1fc; font-size: 14px; font-family: inherit;
}
.field-input:focus { outline: none; border-color: #4f7dff; }
.textarea { resize: none; }
.char-count { align-self: flex-end; font-size: 10px; color: rgba(195,197,215,0.5); }
.info-text { font-size: 12px; color: rgba(195,197,215,0.6); line-height: 1.5; margin: 0; }
.save-btn {
  padding: 14px; border-radius: 12px; background: linear-gradient(90deg, #4f7dff, #3d66d6);
  color: #00297a; font-weight: 700; border: none; cursor: pointer;
}
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.saved-text { text-align: center; font-size: 12px; color: #34d399; margin: 0; }
</style>
