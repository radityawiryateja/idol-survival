<template>
  <div class="tasks-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
    />

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat misi..." />

      <template v-else>
        <!-- Progress rings -->
        <section class="progress-card">
          <div class="progress-inner">
            <div class="rings-wrap">
              <svg viewBox="0 0 100 100" class="rings-svg">
                <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8" />
                <circle
                  cx="50" cy="50" r="45" fill="none" stroke="url(#gradPrimary)"
                  stroke-width="8" stroke-linecap="round"
                  :stroke-dasharray="ringCircumference(45)"
                  :stroke-dashoffset="ringOffset(45, rings.xp)"
                  class="ring-circle"
                />
                <circle cx="50" cy="50" r="34" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8" />
                <circle
                  cx="50" cy="50" r="34" fill="none" stroke="url(#gradSecondary)"
                  stroke-width="8" stroke-linecap="round"
                  :stroke-dasharray="ringCircumference(34)"
                  :stroke-dashoffset="ringOffset(34, rings.supporter)"
                  class="ring-circle"
                />
                <circle cx="50" cy="50" r="23" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="8" />
                <circle
                  cx="50" cy="50" r="23" fill="none" stroke="#FFD700"
                  stroke-width="8" stroke-linecap="round"
                  :stroke-dasharray="ringCircumference(23)"
                  :stroke-dashoffset="ringOffset(23, rings.streak)"
                  class="ring-circle"
                />
                <defs>
                  <linearGradient id="gradPrimary" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#4F7DFF" />
                    <stop offset="100%" stop-color="#3D66D6" />
                  </linearGradient>
                  <linearGradient id="gradSecondary" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#c5c0ff" />
                    <stop offset="100%" stop-color="#3c24c5" />
                  </linearGradient>
                </defs>
              </svg>
              <div class="rings-center">
                <span class="material-symbols-outlined">bolt</span>
              </div>
            </div>

            <div class="progress-details">
              <div>
                <p class="detail-label">XP PROGRESS</p>
                <div class="detail-value-row">
                  <span class="detail-value">{{ rings.xp.current }}</span>
                  <span class="detail-max">/ {{ formatShort(rings.xp.max) }}</span>
                </div>
              </div>
              <div class="side-stats">
                <div class="side-stat">
                  <p class="side-label supporter">SUPPORTER</p>
                  <p class="side-value">{{ rings.supporter.current }}</p>
                </div>
                <div class="side-stat bordered">
                  <p class="side-label streak">STREAK</p>
                  <p class="side-value">{{ rings.streak.current }}D</p>
                </div>
              </div>
            </div>
          </div>

          <div class="pass-row">
            <div class="pass-info">
              <span class="material-symbols-outlined pass-icon">stars</span>
              <div>
                <p class="pass-title">Season Pass Level {{ seasonPass.level }}</p>
                <p class="pass-subtitle">{{ seasonPass.xpToNext }} XP until Level {{ seasonPass.level + 1 }}</p>
              </div>
            </div>
            <span class="material-symbols-outlined chevron">chevron_right</span>
          </div>
        </section>

        <!-- Daily missions -->
        <section class="missions-section">
          <div class="section-head">
            <h2>Daily Missions</h2>
            <span class="reset-timer">Resets in {{ resetsIn }}</span>
          </div>

          <div v-for="mission in dailyMissions" :key="mission.id" class="mission-card">
            <div class="mission-icon" :class="`icon-${mission.color}`">
              <span class="material-symbols-outlined">{{ mission.icon }}</span>
            </div>
            <div class="mission-body">
              <div class="mission-top">
                <h3>{{ mission.title }}</h3>
                <div class="mission-reward" :class="`reward-${mission.color}`">
                  <span class="material-symbols-outlined reward-icon">{{ mission.rewardIcon }}</span>
                  <span>+{{ mission.rewardAmount }}</span>
                </div>
              </div>
              <div class="mission-progress-track">
                <div
                  class="mission-progress-fill"
                  :class="`fill-${mission.color}`"
                  :style="{ width: mission.progressPercent + '%' }"
                ></div>
              </div>
              <p class="mission-status" :class="{ ready: mission.status === 'ready' }">
                {{ mission.statusText }}
              </p>
            </div>
            <button
              class="mission-action"
              :class="actionClass(mission.status)"
              :disabled="mission.status === 'claimed' || (mission.status === 'pending' && mission.validationType !== 'manual')"
              @click="handleMissionAction(mission)"
            >
              {{ actionLabel(mission.status) }}
            </button>
          </div>
        </section>

        <!-- Weekly milestone -->
        <section class="weekly-section">
          <h2>Weekly Reward</h2>
          <div class="chest-card">
            <div class="chest-top">
              <div>
                <p class="chest-title">Super Chest</p>
                <p class="chest-subtitle">Collect {{ weeklyChest.target }} XP to unlock</p>
              </div>
              <div class="chest-icon-wrap">
                <div class="chest-glow"></div>
                <span class="material-symbols-outlined chest-icon">card_giftcard</span>
              </div>
            </div>
            <div class="chest-progress">
              <div class="chest-progress-labels">
                <span>{{ weeklyChest.current }} / {{ weeklyChest.target }} XP</span>
                <span class="chest-percent">{{ chestPercent }}%</span>
              </div>
              <div class="chest-track">
                <div class="chest-fill" :style="{ width: chestPercent + '%' }"></div>
              </div>
            </div>
          </div>
        </section>
      </template>
    </main>

    <BottomNav />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../lib/api'
import { getUser } from '../lib/auth'
import TopAppBar from './TopAppBar.vue'
import BottomNav from './BottomNav.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const profile = ref({ name: 'Producer', tier: 'DIAMOND SUPPORTER', level: 1, avatarUrl: '' })
const loading = ref(true)

const rings = ref({
  xp: { current: 0, max: 3000 },
  supporter: { current: 0, max: 1000 },
  streak: { current: 0, max: 30 },
})

const seasonPass = ref({ level: 1, xpToNext: 0 })
const resetsIn = ref('')
const dailyMissions = ref([])
const weeklyChest = ref({ current: 0, target: 500 })

const chestPercent = computed(() =>
  Math.min(100, Math.round((weeklyChest.value.current / weeklyChest.value.target) * 100))
)

// Converts a ring's current/max into an SVG stroke-dashoffset so the arc
// visually represents the percentage complete.
function ringCircumference(radius) {
  return 2 * Math.PI * radius
}
function ringOffset(radius, ring) {
  const circumference = ringCircumference(radius)
  const percent = Math.min(1, ring.current / ring.max)
  return circumference * (1 - percent)
}

function formatShort(n) {
  return n >= 1000 ? `${(n / 1000).toFixed(n % 1000 === 0 ? 0 : 1)}k` : n
}

function actionLabel(mission) {
  if (mission.status === 'claimed') return 'CLAIMED'
  if (mission.status === 'ready') return 'CLAIM'
  if (mission.validationType === 'manual') return 'SHARE'
  return 'AUTO'
}

function actionClass(mission) {
  if (mission.status === 'claimed') return 'action-claimed'
  if (mission.status === 'ready') return 'action-ready'
  if (mission.validationType === 'manual') return 'action-go'
  return 'action-auto'
}

async function handleMissionAction(mission) {
  if (mission.status === 'claimed') return

  if (mission.status === 'ready') {
    try {
      const { data } = await api.post(`/tasks/${mission.id}/claim`)
      mission.status = data.status
      mission.statusText = data.statusText
      mission.progressPercent = data.progressPercent
    } catch (err) {
      alert(err.response?.data?.detail || 'Gagal klaim misi')
    }
    return
  }

  // Status masih 'pending' — cuma tipe 'manual' yang boleh dipicu manual.
  if (mission.validationType !== 'manual') return

  if (navigator.share) {
    try {
      await navigator.share({
        title: 'Idol Survival',
        text: 'Cek ranking terbaru di Idol Survival!',
        url: window.location.origin,
      })
    } catch {
      return // user batal share
    }
  }

  try {
    const { data } = await api.post(`/tasks/${mission.id}/share`)
    mission.status = data.status
    mission.statusText = data.statusText
    mission.progressPercent = data.progressPercent
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal update misi')
  }
}

async function loadTasks() {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }

  loading.value = true
  try {
    const { data } = await api.get('/tasks/summary')
    rings.value = data.rings
    seasonPass.value = data.seasonPass
    resetsIn.value = data.resetsIn
    dailyMissions.value = data.dailyMissions
    weeklyChest.value = data.weeklyChest
  } catch (err) {
    console.error('Failed to load tasks', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadTasks)
</script>

<style scoped>
.tasks-page {
  min-height: 100dvh;
  padding-bottom: 128px;
  background: #0d1226;
  color: #dce1fc;
}
.content {
  max-width: 480px;
  margin: 0 auto;
  padding: 96px 20px 0;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Progress card */
.progress-card {
  border-radius: 32px;
  padding: 24px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}
.progress-inner {
  display: flex;
  align-items: center;
  gap: 24px;
}
.rings-wrap {
  position: relative;
  width: 128px;
  height: 128px;
  flex-shrink: 0;
}
.rings-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.ring-circle {
  transition: stroke-dashoffset 0.8s ease-in-out;
}
.rings-center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b5c4ff;
  font-size: 32px;
}
.progress-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
  margin: 0 0 4px;
}
.detail-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}
.detail-value {
  font-size: 24px;
  font-weight: 600;
  color: #b5c4ff;
}
.detail-max {
  font-size: 14px;
  color: #c3c5d7;
}
.side-stats {
  display: flex;
  gap: 16px;
}
.side-stat.bordered {
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  padding-left: 16px;
}
.side-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin: 0;
}
.side-label.supporter { color: #c5c0ff; }
.side-label.streak { color: #fbbf24; }
.side-value {
  font-size: 14px;
  font-weight: 700;
  color: #dce1fc;
  margin: 2px 0 0;
}
.pass-row {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.pass-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.pass-icon { color: #638aff; }
.pass-title {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
  color: #dce1fc;
}
.pass-subtitle {
  font-size: 12px;
  color: #c3c5d7;
  margin: 0;
}
.chevron { color: #c3c5d7; }

/* Missions */
.missions-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.section-head h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.reset-timer {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #b5c4ff;
}
.mission-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.mission-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-primary { background: rgba(181, 196, 255, 0.1); color: #b5c4ff; }
.icon-secondary { background: rgba(197, 192, 255, 0.2); color: #c5c0ff; }
.icon-tertiary { background: rgba(126, 141, 210, 0.2); color: #b8c4ff; }
.icon-neutral { background: rgba(255, 255, 255, 0.05); color: #dce1fc; }
.mission-body { flex: 1; min-width: 0; }
.mission-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.mission-top h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: #dce1fc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mission-reward {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  margin-left: 8px;
}
.reward-icon { font-size: 16px; }
.reward-primary { color: #b5c4ff; }
.reward-secondary { color: #c5c0ff; }
.reward-tertiary { color: #b8c4ff; }
.mission-progress-track {
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
  margin-bottom: 8px;
}
.mission-progress-fill { height: 100%; }
.fill-primary { background: #b5c4ff; }
.fill-secondary { background: #3c24c5; }
.fill-tertiary { background: #7e8dd2; }
.mission-status {
  font-size: 12px;
  color: #c3c5d7;
  margin: 0;
}
.action-auto {
  background: rgba(255, 255, 255, 0.03);
  color: rgba(195, 197, 215, 0.4);
  cursor: default;
}
.mission-status.ready {
  color: #b5c4ff;
  font-weight: 700;
}
.mission-action {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  border: none;
  cursor: pointer;
  flex-shrink: 0;
}
.action-go {
  background: #b5c4ff;
  color: #00297a;
  box-shadow: 0 4px 12px rgba(79, 125, 255, 0.3);
}
.action-ready {
  background: #638aff;
  color: #00236c;
  box-shadow: 0 4px 12px rgba(79, 125, 255, 0.2);
}
.action-claimed {
  background: rgba(255, 255, 255, 0.05);
  color: #c3c5d7;
  opacity: 0.5;
  cursor: not-allowed;
}

/* Weekly chest */
.weekly-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.weekly-section h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.chest-card {
  border-radius: 24px;
  padding: 16px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}
.chest-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.chest-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #dce1fc;
}
.chest-subtitle {
  font-size: 14px;
  color: #c3c5d7;
  margin: 4px 0 0;
}
.chest-icon-wrap {
  position: relative;
  width: 64px;
  height: 64px;
}
.chest-glow {
  position: absolute;
  inset: 0;
  background: rgba(181, 196, 255, 0.2);
  border-radius: 50%;
  filter: blur(20px);
  animation: chest-pulse 3s infinite ease-in-out;
}
@keyframes chest-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
.chest-icon {
  position: relative;
  z-index: 1;
  font-size: 48px;
  color: #b5c4ff;
}
.chest-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.chest-progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #dce1fc;
}
.chest-percent { color: #b5c4ff; }
.chest-track {
  height: 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}
.chest-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #b5c4ff, #3c24c5);
  transition: width 0.4s ease;
}
</style>
