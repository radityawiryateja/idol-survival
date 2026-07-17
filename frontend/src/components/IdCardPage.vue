<template>
  <div class="idcard-page">
    <!-- Custom header (beda dari TopAppBar biasa — ada tombol back) -->
    <header class="top-bar">
      <button class="back-btn" @click="goBack" aria-label="Back">
        <span class="material-symbols-outlined">arrow_back_ios_new</span>
      </button>
      <h1 class="bar-title">IDOL SURVIVAL</h1>
      <div class="bar-avatar">
        <img :src="profile.avatarUrl" :alt="profile.name" />
      </div>
    </header>

    <main class="content">
      <div class="id-card holographic-sheen">
        <!-- Card header -->
        <div class="card-top">
          <div class="season-block">
            <span class="season-label">{{ idol.seasonLabel }}</span>
            <div class="project-row">
              <div class="project-badge">
                <span class="material-symbols-outlined">star</span>
              </div>
              <span class="project-name">{{ idol.projectName }}</span>
            </div>
          </div>
          <div class="level-block">
            <span class="level-label">LEVEL</span>
            <span class="level-value">{{ idol.level }}</span>
          </div>
        </div>

        <!-- Portrait -->
        <div class="portrait-wrap">
          <img :src="idol.photo" :alt="idol.name" class="portrait" />
          <div class="verified-badge">
            <span class="material-symbols-outlined">verified</span>
            <span>VERIFIED</span>
          </div>
          <div class="portrait-overlay">
            <h2 class="idol-name">{{ idol.name }}</h2>
            <span class="idol-code">{{ idol.code }}</span>
          </div>
        </div>

        <!-- Meta grid -->
        <div class="meta-grid">
          <div class="meta-item">
            <span class="meta-label">AGENCY</span>
            <span class="meta-value">{{ idol.agency }}</span>
          </div>
          <div class="meta-item align-right">
            <span class="meta-label">ENROLLMENT</span>
            <span class="meta-value">{{ idol.enrollmentDate }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">SPECIALTY</span>
            <span class="meta-value">{{ idol.specialty }}</span>
          </div>
          <div class="meta-item align-right">
            <span class="meta-label">STATUS</span>
            <div class="status-row">
              <span class="status-dot"></span>
              <span class="meta-value status-value">{{ idol.status }}</span>
            </div>
          </div>
        </div>

        <!-- Auth footer -->
        <div class="auth-footer">
          <div class="qr-block">
            <div class="qr-box">
              <img :src="idol.qrCodeUrl" alt="QR code" />
            </div>
            <div class="token-block">
              <span class="token-label">Auth Token: {{ idol.authToken }}</span>
              <div class="barcode-strip"></div>
            </div>
          </div>

          <div class="signature-block">
            <div class="signature-text">
              <p class="signature-name">{{ idol.directorSignature }}</p>
              <div class="signature-line"></div>
              <span class="signature-caption">DIRECTOR SIGNATURE</span>
            </div>
            <button
              class="sync-btn"
              :class="{ syncing: syncState === 'syncing', synced: syncState === 'synced' }"
              :disabled="syncState === 'syncing'"
              @click="handleSync"
            >
              <span class="material-symbols-outlined" :class="{ spin: syncState === 'syncing' }">
                {{ syncIcon }}
              </span>
              {{ syncLabel }}
            </button>
          </div>
        </div>
      </div>

      <p class="legend-text">
        This digital identification is property of the Survival Program. Unauthorized
        replication or transfer of this token will result in immediate disqualification
        and removal from the training facility.
      </p>
    </main>

    <BottomNav />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../lib/api'
import { getUser } from '../lib/auth'
import BottomNav from './BottomNav.vue'

const route = useRoute()
const router = useRouter()

const profile = ref({ name: 'Producer', avatarUrl: '' })

const idol = ref({
  seasonLabel: '',
  projectName: '',
  level: '',
  photo: '',
  name: '',
  code: '',
  agency: '',
  enrollmentDate: '',
  specialty: '',
  status: '',
  qrCodeUrl: '',
  authToken: '',
  directorSignature: '',
})

// idle -> syncing -> synced -> (auto reverts to idle after a moment)
const syncState = ref('idle')

const syncLabel = computed(() => {
  if (syncState.value === 'syncing') return 'SYNCING...'
  if (syncState.value === 'synced') return 'SYNCED'
  return 'TAP TO SYNC'
})

const syncIcon = computed(() => {
  if (syncState.value === 'syncing') return 'sync'
  if (syncState.value === 'synced') return 'check_circle'
  return 'nfc'
})

function goBack() {
  router.back()
}

async function handleSync() {
  if (syncState.value === 'syncing') return

  syncState.value = 'syncing'
  try {
    await api.post(`/idols/${route.params.id}/sync`)
    syncState.value = 'synced'
  } catch (err) {
    console.error('Failed to sync ID card', err)
    syncState.value = 'idle'
    return
  }

  setTimeout(() => {
    syncState.value = 'idle'
  }, 2000)
}

async function loadIdCard() {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }

  try {
    const { data } = await api.get(`/idols/${route.params.id}/card`)
    idol.value = data
  } catch (err) {
    console.error('Failed to load ID card', err)
  }
}

onMounted(loadIdCard)
</script>

<style scoped>
.idcard-page {
  min-height: 100dvh;
  padding-bottom: 128px;
  background: #0d1226;
  color: #dce1fc;
}

/* Header */
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 50;
  background: rgba(13, 18, 38, 0.8);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 20px;
  max-width: 480px;
  margin: 0 auto;
}
.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: none;
  border: none;
  color: #b5c4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.back-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}
.bar-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0;
}
.bar-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.bar-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #191f32;
}

/* Content */
.content {
  max-width: 480px;
  margin: 0 auto;
  padding: 96px 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

/* ID card shell */
.id-card {
  width: 100%;
  position: relative;
  overflow: hidden;
  border-radius: 32px;
  padding: 24px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.holographic-sheen::after {
  content: '';
  position: absolute;
  inset: -100%;
  background: linear-gradient(
    135deg,
    rgba(79, 125, 255, 0) 40%,
    rgba(79, 125, 255, 0.1) 45%,
    rgba(197, 192, 255, 0.2) 50%,
    rgba(79, 125, 255, 0.1) 55%,
    rgba(79, 125, 255, 0) 60%
  );
  animation: holo-swipe 6s ease-in-out infinite;
  pointer-events: none;
}
@keyframes holo-swipe {
  0% { transform: translate(-30%, -30%); }
  100% { transform: translate(30%, 30%); }
}

/* Card header */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.season-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #b5c4ff;
  display: block;
}
.project-row {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}
.project-badge {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background: #b5c4ff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.project-badge .material-symbols-outlined {
  font-size: 14px;
  color: #00297a;
  font-variation-settings: 'FILL' 1;
}
.project-name {
  font-size: 18px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: -0.02em;
  color: #dce1fc;
}
.level-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.level-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
}
.level-value {
  font-size: 18px;
  font-weight: 700;
  color: #b5c4ff;
}

/* Portrait */
.portrait-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 5;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.portrait {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(0.2) contrast(1.1);
}
.verified-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(181, 196, 255, 0.9);
  color: #00297a;
  padding: 4px 12px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  gap: 4px;
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.verified-badge .material-symbols-outlined {
  font-size: 16px;
  font-variation-settings: 'FILL' 1;
}
.verified-badge span:last-child {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.portrait-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 16px;
  background: linear-gradient(to top, #070d20, transparent);
}
.idol-name {
  font-size: 34px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #fff;
  margin: 0;
  line-height: 1;
}
.idol-code {
  font-size: 16px;
  color: #dbe1ff;
}

/* Meta grid */
.meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  padding: 8px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.meta-item {
  display: flex;
  flex-direction: column;
}
.meta-item.align-right {
  align-items: flex-end;
  text-align: right;
}
.meta-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
  margin-bottom: 4px;
}
.meta-value {
  font-size: 16px;
  font-weight: 700;
  color: #dce1fc;
}
.status-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4f7dff;
  box-shadow: 0 0 10px #4f7dff;
  animation: status-pulse 2s infinite;
}
@keyframes status-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.status-value { color: #b5c4ff; }

/* Auth footer */
.auth-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
}
.qr-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.qr-box {
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 8px;
  padding: 8px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}
.qr-box img {
  width: 100%;
  height: 100%;
}
.token-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.token-label {
  font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  color: #c3c5d7;
}
.barcode-strip {
  height: 16px;
  width: 128px;
  opacity: 0.6;
  background-image: repeating-linear-gradient(
    90deg,
    #dce1fc,
    #dce1fc 1px,
    transparent 1px,
    transparent 4px,
    #dce1fc 4px,
    #dce1fc 6px,
    transparent 6px,
    transparent 9px
  );
}
.signature-block {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}
.signature-text {
  text-align: right;
}
.signature-name {
  font-family: 'JetBrains Mono', monospace;
  font-style: italic;
  font-size: 14px;
  color: #c3c5d7;
  margin: 0 0 -4px;
}
.signature-line {
  height: 1px;
  width: 128px;
  background: rgba(195, 197, 215, 0.3);
  margin-left: auto;
}
.signature-caption {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: rgba(195, 197, 215, 0.5);
}
.sync-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 12px;
  background: #b5c4ff;
  color: #00297a;
  font-weight: 700;
  font-size: 13px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 24px rgba(79, 125, 255, 0.4);
}
.sync-btn:active {
  transform: scale(0.96);
}
.sync-btn.syncing {
  opacity: 0.8;
  cursor: wait;
}
.sync-btn.synced {
  background: #34d399;
  color: #062e23;
}
.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Legend */
.legend-text {
  font-size: 12px;
  color: rgba(195, 197, 215, 0.6);
  text-align: center;
  line-height: 1.6;
  padding: 0 16px;
}
</style>
