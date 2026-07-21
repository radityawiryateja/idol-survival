<template>
  <div class="settings-page">
    <header class="top-bar">
      <button class="back-btn" @click="$router.back()" aria-label="Back">
        <span class="material-symbols-outlined">arrow_back_ios_new</span>
      </button>
      <h2>Notifications</h2>
      <div class="spacer"></div>
    </header>

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat pengaturan..." />

      <template v-else>
        <div v-for="item in toggleItems" :key="item.key" class="toggle-row">
          <div class="toggle-info">
            <span class="material-symbols-outlined toggle-icon">{{ item.icon }}</span>
            <div>
              <p class="toggle-title">{{ item.title }}</p>
              <p class="toggle-subtitle">{{ item.subtitle }}</p>
            </div>
          </div>
          <button
            class="switch"
            :class="{ on: prefs[item.key] }"
            @click="toggle(item.key)"
            :aria-pressed="prefs[item.key]"
          >
            <span class="knob"></span>
          </button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../lib/api'
import LoadingSpinner from './LoadingSpinner.vue'

const loading = ref(true)
const prefs = ref({
  voteReminders: true,
  missionReminders: true,
  liveBroadcastAlerts: true,
  chatMessageAlerts: true,
})

const toggleItems = [
  { key: 'voteReminders', icon: 'how_to_reg', title: 'Vote Reminders', subtitle: 'Pengingat sebelum voting window ditutup' },
  { key: 'missionReminders', icon: 'assignment', title: 'Mission Reminders', subtitle: 'Notif misi harian belum selesai' },
  { key: 'liveBroadcastAlerts', icon: 'sensors', title: 'Live Broadcast Alerts', subtitle: 'Idol favorit mulai siaran/broadcast' },
  { key: 'chatMessageAlerts', icon: 'forum', title: 'Chat Message Alerts', subtitle: 'Balasan baru di Talks' },
]

let saveTimer = null

async function loadPrefs() {
  loading.value = true
  try {
    const { data } = await api.get('/settings/notifications')
    prefs.value = data
  } catch (err) {
    console.error('Failed to load notification settings', err)
  } finally {
    loading.value = false
  }
}

function toggle(key) {
  prefs.value[key] = !prefs.value[key]
  // Debounce save dikit biar nggak nembak API tiap klik beruntun.
  clearTimeout(saveTimer)
  saveTimer = setTimeout(savePrefs, 400)
}

async function savePrefs() {
  try {
    await api.patch('/settings/notifications', prefs.value)
  } catch (err) {
    console.error('Failed to save notification settings', err)
  }
}

onMounted(loadPrefs)
</script>

<style scoped>
.settings-page { min-height: 100dvh; background: #0d1226; color: #dce1fc; }
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
  display: flex; flex-direction: column; gap: 12px;
}
.toggle-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px; border-radius: 16px;
  background: rgba(20, 28, 52, 0.8); border: 1px solid rgba(255,255,255,0.1);
}
.toggle-info { display: flex; align-items: center; gap: 14px; }
.toggle-icon { color: #b5c4ff; }
.toggle-title { font-size: 14px; font-weight: 700; margin: 0; color: #dce1fc; }
.toggle-subtitle { font-size: 11px; color: #c3c5d7; margin: 2px 0 0; }
.switch {
  width: 44px; height: 24px; border-radius: 999px; border: none; cursor: pointer;
  background: rgba(255,255,255,0.1); position: relative; flex-shrink: 0; transition: background 0.2s;
}
.switch.on { background: #4f7dff; }
.knob {
  position: absolute; top: 2px; left: 2px; width: 20px; height: 20px; border-radius: 50%;
  background: #fff; transition: transform 0.2s;
}
.switch.on .knob { transform: translateX(20px); }
</style>
