<template>
  <div class="profile-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
      :frame-style="profile.frameStyle"
      :frame-asset-url="profile.frameAssetUrl"
    />

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat profil..." />

      <template v-else>
        <!-- Profile header -->
        <section class="profile-header">
          <div class="avatar-glow"></div>
          <div class="avatar-wrap">
            <div class="avatar-ring">
              <div class="avatar-inner">
                <img :src="profile.avatarUrl" :alt="profile.name" />
              </div>
            </div>
            <span class="level-badge">LVL {{ profile.level }}</span>
          </div>

          <div class="identity">
            <div class="name-row">
              <h1>{{ profile.name }}</h1>
              <span v-if="profile.verified" class="material-symbols-outlined verified-icon">verified</span>
            </div>
            <span class="tier-badge">{{ profile.tier }}</span>
          </div>

          <div class="xp-bar-wrap">
            <div class="xp-labels">
              <span>Producer XP</span>
              <span>{{ profile.xp.current }} / {{ profile.xp.max }}</span>
            </div>
            <div class="xp-track">
              <div class="xp-fill" :style="{ width: xpPercent + '%' }"></div>
            </div>
          </div>
        </section>

        <!-- Stats bento grid -->
        <section class="stats-grid">
          <div class="stat-box">
            <div class="stat-label">
              <span class="material-symbols-outlined">how_to_reg</span>
              <span>VOTES CAST</span>
            </div>
            <span class="stat-value">{{ profile.votesCast }}</span>
          </div>
          <div class="stat-box">
            <div class="stat-label">
              <span class="material-symbols-outlined">diamond</span>
              <span>DIAMONDS</span>
            </div>
            <span class="stat-value">{{ profile.diamonds }}</span>
          </div>
          <div class="stat-box wide">
            <div class="achievements-info">
              <div class="stat-label">
                <span class="material-symbols-outlined">military_tech</span>
                <span>ACHIEVEMENTS</span>
              </div>
              <span class="stat-value">{{ profile.achievementsUnlocked }} Unlocked</span>
            </div>
            <div class="achievement-icons">
              <div v-for="badge in profile.recentBadges" :key="badge.icon" class="badge-circle">
                <span class="material-symbols-outlined" :class="`badge-${badge.color}`">{{ badge.icon }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Role-specific shortcut (hanya muncul untuk role terkait) -->
        <router-link v-if="role === 'admin'" to="/admin" class="role-banner admin">
          <span class="material-symbols-outlined">admin_panel_settings</span>
          <span>Buka Admin Panel</span>
          <span class="material-symbols-outlined chevron">chevron_right</span>
        </router-link>
        <router-link v-else-if="role === 'idol'" to="/idol-panel" class="role-banner idol">
          <span class="material-symbols-outlined">stars</span>
          <span>Buka Idol Panel</span>
          <span class="material-symbols-outlined chevron">chevron_right</span>
        </router-link>

        <!-- Settings list -->
        <section class="settings-section">
          <h2>ACCOUNT PREFERENCES</h2>

          <button
            v-for="item in settingsItems"
            :key="item.title"
            class="settings-row"
            @click="handleSettingsClick(item)"
          >
            <div class="settings-left">
              <div class="settings-icon" :class="`icon-${item.color}`">
                <span class="material-symbols-outlined">{{ item.icon }}</span>
              </div>
              <div class="settings-text">
                <span class="settings-title">{{ item.title }}</span>
                <span class="settings-subtitle">{{ item.subtitle }}</span>
              </div>
            </div>
            <span class="material-symbols-outlined chevron">chevron_right</span>
          </button>

          <button class="settings-row logout-row" @click="handleLogout">
            <div class="settings-left">
              <div class="settings-icon icon-error">
                <span class="material-symbols-outlined">logout</span>
              </div>
              <div class="settings-text">
                <span class="settings-title logout-title">Logout</span>
                <span class="settings-subtitle logout-subtitle">End current session</span>
              </div>
            </div>
          </button>
        </section>

        <div class="version-footer">
          <span>IDOL SURVIVAL — BUILD {{ buildVersion }}</span>
        </div>
      </template>
    </main>

    <BottomNav />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { cachedApiGet } from '../lib/api'
import { clearSession, getRole, getUser, getFrame } from '../lib/auth'
import { cacheClearAll } from '../lib/cache'
import TopAppBar from './TopAppBar.vue'
import BottomNav from './BottomNav.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const router = useRouter()

const profile = ref({
  name: 'Producer',
  tier: 'PLATINUM MEMBER',
  level: 1,
  avatarUrl: '',
  verified: false,
  xp: { current: 0, max: 2000 },
  votesCast: 0,
  diamonds: 0,
  achievementsUnlocked: 0,
  recentBadges: [],
  frameStyle: 'none',
  frameAssetUrl: ''
})

const loading = ref(true)
const buildVersion = ref('4.8.2-PRO')
const role = ref(getRole())

const settingsItems = [
  {
    title: 'My Avatars',
    subtitle: 'Pakai avatar limited hasil beli di Shop',
    icon: 'face',
    color: 'primary',
    route: '/avatars',
  },
  {
    title: 'Account Settings',
    subtitle: 'Email, Password, Security',
    icon: 'person_outline',
    color: 'primary',
    route: '/settings/account',
  },
  {
    title: 'Notifications',
    subtitle: 'Push alerts, Voting reminders',
    icon: 'notifications_active',
    color: 'secondary',
    route: '/settings/notifications',
  },
  {
    title: 'Appearance',
    subtitle: 'Theme, Visual effects, Layout',
    icon: 'palette',
    color: 'tertiary',
    route: '/settings/appearance',
  },
]

const xpPercent = computed(() =>
  Math.min(100, Math.round((profile.value.xp.current / profile.value.xp.max) * 100))
)

function handleSettingsClick(item) {
  router.push(item.route)
}

// Clears the local session and tells the backend to invalidate it too,
// then always redirects to login regardless of whether the network call
// succeeds — the person shouldn't get stuck logged in on the client.
async function handleLogout() {
  try {
    await api.post('/auth/logout')
  } catch (err) {
    console.error('Logout request failed, clearing session locally anyway', err)
  } finally {
    clearSession()
    cacheClearAll() // jangan sampai data producer sebelumnya bocor ke akun berikutnya
    router.push({ name: 'login' })
  }
}

async function loadProfile() {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }
  role.value = getRole()

  const cachedFrame = getFrame()
  if (cachedFrame) {
    profile.value.frameStyle = cachedFrame.style
    profile.value.frameAssetUrl = cachedFrame.assetUrl
  }

  loading.value = true
  try {
    const data = await cachedApiGet('/profile/me', { ttl: 60 * 1000 })
    profile.value = { ...profile.value, ...data }
  } catch (err) {
    console.error('Failed to load profile', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
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
  gap: 24px;
}

/* Profile header */
.profile-header {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}
.avatar-glow {
  position: absolute;
  top: -48px;
  left: 50%;
  transform: translateX(-50%);
  width: 256px;
  height: 256px;
  background: rgba(181, 196, 255, 0.05);
  border-radius: 50%;
  filter: blur(60px);
  z-index: -1;
}
.avatar-wrap {
  position: relative;
}
.avatar-ring {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  padding: 4px;
  background: linear-gradient(to top right, #b5c4ff, #3c24c5);
}
.avatar-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 4px solid #0d1226;
  overflow: hidden;
}
.avatar-inner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #191f32;
}
.level-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: #b5c4ff;
  color: #00297a;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  border: 2px solid #0d1226;
}
.identity {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.name-row h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #dce1fc;
}
.verified-icon {
  color: #b5c4ff;
  font-size: 18px;
  font-variation-settings: 'FILL' 1;
}
.tier-badge {
  background: rgba(60, 36, 197, 0.3);
  color: #b2acff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 4px 12px;
  border-radius: 999px;
}
.xp-bar-wrap {
  width: 100%;
  max-width: 320px;
  padding-top: 16px;
}
.xp-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
  padding: 0 4px;
  margin-bottom: 4px;
}
.xp-track {
  height: 6px;
  border-radius: 999px;
  background: #191f32;
  overflow: hidden;
}
.xp-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #b5c4ff, #c5c0ff);
  box-shadow: 0 0 12px rgba(79, 125, 255, 0.4);
  transition: width 0.4s ease;
}

/* Stats bento */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.stat-box {
  border-radius: 12px;
  padding: 24px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.stat-box.wide {
  grid-column: span 2;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.stat-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
}
.stat-label .material-symbols-outlined {
  color: #b5c4ff;
  font-size: 16px;
}
.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #dce1fc;
}
.achievements-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.achievement-icons {
  display: flex;
}
.badge-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #191f32;
  background: #2e3449;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: -12px;
}
.badge-circle .material-symbols-outlined { font-size: 16px; }
.badge-primary { color: #b5c4ff; }
.badge-secondary { color: #c5c0ff; }
.badge-tertiary { color: #b8c4ff; }

/* Role shortcut banner */
.role-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 700;
}
.role-banner .chevron { margin-left: auto; }
.role-banner.admin {
  background: rgba(255, 180, 171, 0.1);
  border: 1px solid rgba(255, 180, 171, 0.3);
  color: #ffb4ab;
}
.role-banner.idol {
  background: rgba(181, 196, 255, 0.1);
  border: 1px solid rgba(181, 196, 255, 0.3);
  color: #b5c4ff;
}

/* Settings */
.settings-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.settings-section h2 {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
  padding: 0 4px;
  margin: 0 0 16px;
}
.settings-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-radius: 12px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-left: none;
  border-right: none;
  border-bottom: none;
  margin-bottom: 4px;
  cursor: pointer;
  transition: background 0.15s;
}
.settings-row:hover {
  background: rgba(255, 255, 255, 0.05);
}
.settings-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.settings-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-primary { background: rgba(181, 196, 255, 0.1); color: #b5c4ff; }
.icon-secondary { background: rgba(197, 192, 255, 0.1); color: #c5c0ff; }
.icon-tertiary { background: rgba(184, 196, 255, 0.1); color: #b8c4ff; }
.icon-error { background: rgba(255, 180, 171, 0.1); color: #ffb4ab; }
.settings-text {
  display: flex;
  flex-direction: column;
  text-align: left;
}
.settings-title {
  font-size: 16px;
  font-weight: 600;
  color: #dce1fc;
}
.settings-subtitle {
  font-size: 12px;
  color: #c3c5d7;
}
.chevron {
  color: #c3c5d7;
  transition: transform 0.15s;
}
.settings-row:hover .chevron {
  transform: translateX(4px);
}
.logout-row {
  margin-top: 16px;
}
.logout-title { color: #ffb4ab; }
.logout-subtitle { color: rgba(255, 180, 171, 0.6); }

.version-footer {
  text-align: center;
  padding: 16px 0;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: rgba(195, 197, 215, 0.4);
}
</style>
