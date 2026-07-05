<template>
  <div class="dashboard-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
    />

    <main class="content">
      <section class="hero-card">
        <div class="hero-top">
          <div>
            <p class="season-label">SURVIVAL SEASON 04</p>
            <h2 class="hero-title">REBIRTH OF THE STAR</h2>
          </div>
          <div class="days-left">{{ season.daysLeft }} DAYS LEFT</div>
        </div>

        <div class="stats-grid">
          <div class="stat-box">
            <div class="stat-label">
              <span class="material-symbols-outlined">confirmation_number</span>VOTE TICKETS
            </div>
            <p class="stat-value">{{ stats.voteTickets }}</p>
          </div>
          <div class="stat-box">
            <div class="stat-label">
              <span class="material-symbols-outlined">diamond</span>DIAMONDS
            </div>
            <p class="stat-value">{{ stats.diamonds }}</p>
          </div>
        </div>

        <div class="hero-footer">
          <div>
            <span class="supporter-label">SUPPORTER POINTS</span>
            <div class="progress-row">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: supporterPercent + '%' }"></div>
              </div>
              <span class="progress-text">{{ stats.supporterPoints }} / {{ stats.supporterCap }}</span>
            </div>
          </div>
          <div class="live-badge"><span class="dot"></span>LIVE NOW</div>
        </div>
      </section>

      <section class="action-grid">
        <router-link
          v-for="action in actions"
          :key="action.label"
          :to="action.to"
          class="action-item"
        >
          <div class="action-icon" :class="{ primary: action.primary }">
            <span class="material-symbols-outlined">{{ action.icon }}</span>
          </div>
          <span class="action-label">{{ action.label }}</span>
        </router-link>
      </section>

      <section class="live-banner" :style="bannerStyle">
        <div class="banner-overlay"></div>
        <div class="banner-content">
          <span class="banner-tag">LIVE PERFORMANCE</span>
          <h3>{{ liveBanner.title }}</h3>
          <p>{{ liveBanner.viewers }} Viewers Streaming Now</p>
        </div>
      </section>

      <section class="featured-idols">
        <div class="section-head">
          <h3>FEATURED IDOLS</h3>
          <router-link to="/idols" class="see-all">SEE ALL</router-link>
        </div>
        <div class="idols-scroll">
          <router-link
            v-for="idol in featuredIdols"
            :key="idol.id"
            :to="`/idols/${idol.id}`"
            class="idol-card"
          >
            <img :src="idol.photo" :alt="idol.name" />
            <span class="rank-badge">RANK {{ idol.rank }}</span>
            <span class="idol-name">{{ idol.name }}</span>
          </router-link>
        </div>
      </section>

      <section class="missions">
        <h3>TODAY'S MISSIONS</h3>
        <div
          v-for="mission in missions"
          :key="mission.title"
          class="mission-card"
          :class="{ highlighted: mission.highlighted }"
        >
          <div class="mission-info">
            <div class="mission-icon">
              <span class="material-symbols-outlined">{{ mission.icon }}</span>
            </div>
            <div>
              <h4>{{ mission.title }}</h4>
              <p>{{ mission.reward }}</p>
            </div>
          </div>
          <button class="mission-btn" :class="{ active: mission.highlighted }">GO</button>
        </div>
      </section>
    </main>

    <BottomNav />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../lib/api'
import { getUser } from '../lib/auth'
import BottomNav from './BottomNav.vue'
import TopAppBar from './TopAppBar.vue'

const profile = ref({
  name: 'Producer',
  tier: 'DIAMOND SUPPORTER',
  level: 1,
  avatarUrl: '',
})

const season = ref({ daysLeft: 0 })
const stats = ref({ voteTickets: 0, diamonds: 0, supporterPoints: 0, supporterCap: 10000 })
const liveBanner = ref({ title: '', viewers: '', image: '' })
const featuredIdols = ref([])
const missions = ref([])

const supporterPercent = computed(() =>
  Math.min(100, Math.round((stats.value.supporterPoints / stats.value.supporterCap) * 100))
)

const bannerStyle = computed(() => ({
  backgroundImage: liveBanner.value.image ? `url(${liveBanner.value.image})` : 'none',
}))

const actions = [
  { label: 'Vote', icon: 'how_to_reg', to: '/vote', primary: true },
  { label: 'Idols', icon: 'groups', to: '/idols' },
  { label: 'Tasks', icon: 'assignment', to: '/tasks' },
  { label: 'Ranks', icon: 'leaderboard', to: '/leaderboard' },
  { label: 'Rewards', icon: 'redeem', to: '/rewards' },
  { label: 'Events', icon: 'event', to: '/events' },
  { label: 'Talk', icon: 'forum', to: '/talk' },
  { label: 'Shop', icon: 'shopping_bag', to: '/shop' },
]

// Loads live dashboard data from the FastAPI backend. Falls back to the
// cached user object (from Telegram login) for the header while the
// request is in flight.
async function loadDashboardData() {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }

  try {
    const { data } = await api.get('/dashboard/summary')
    profile.value = { ...profile.value, ...data.profile }
    season.value = data.season
    stats.value = data.stats
    liveBanner.value = data.liveBanner
    featuredIdols.value = data.featuredIdols
    missions.value = data.missions
  } catch (err) {
    console.error('Failed to load dashboard data', err)
  }
}

onMounted(loadDashboardData)
</script>

<style scoped>
.dashboard-page {
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
.hero-card {
  border-radius: 24px;
  padding: 24px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 20px rgba(79, 125, 255, 0.2);
}
.hero-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.season-label {
  font-size: 11px;
  letter-spacing: 0.05em;
  color: rgba(181, 196, 255, 0.8);
  margin: 0 0 4px;
}
.hero-title {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}
.days-left {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.stat-box {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px;
}
.stat-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #c3c5d7;
  margin-bottom: 4px;
}
.stat-label .material-symbols-outlined {
  font-size: 16px;
}
.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}
.hero-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.supporter-label {
  font-size: 11px;
  color: #c3c5d7;
  display: block;
}
.progress-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
.progress-bar {
  width: 128px;
  height: 6px;
  background: #191f32;
  border-radius: 999px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #b5c4ff, #c5c0ff);
}
.progress-text {
  font-size: 12px;
  font-weight: 700;
  color: #b5c4ff;
}
.live-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 700;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffb4ab;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  50% { opacity: 0.4; }
}
.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: inherit;
}
.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c3c5d7;
}
.action-icon.primary {
  color: #b5c4ff;
  box-shadow: 0 0 20px rgba(79, 125, 255, 0.2);
}
.action-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-align: center;
}
.live-banner {
  position: relative;
  height: 96px;
  border-radius: 16px;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  background-color: #191f32;
}
.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, #0d1226, rgba(13, 18, 38, 0.4), transparent);
}
.banner-content {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 24px;
}
.banner-tag {
  font-size: 11px;
  font-weight: 700;
  color: #ffb4ab;
  margin-bottom: 4px;
}
.banner-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}
.banner-content p {
  font-size: 12px;
  color: #c3c5d7;
  margin: 0;
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.section-head h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}
.see-all {
  font-size: 11px;
  font-weight: 700;
  color: #b5c4ff;
  text-decoration: none;
}
.idols-scroll {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.idol-card {
  position: relative;
  flex-shrink: 0;
  width: 128px;
  height: 176px;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-decoration: none;
  background: #191f32;
}
.idol-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.rank-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(181, 196, 255, 0.9);
  color: #00297a;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}
.idol-name {
  position: absolute;
  bottom: 8px;
  left: 8px;
  right: 8px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
}
.missions h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 12px;
}
.mission-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 12px;
}
.mission-card.highlighted {
  border-left: 4px solid #b5c4ff;
}
.mission-info {
  display: flex;
  align-items: center;
  gap: 16px;
}
.mission-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(181, 196, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b5c4ff;
  flex-shrink: 0;
}
.mission-info h4 {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}
.mission-info p {
  font-size: 12px;
  color: #c3c5d7;
  margin: 0;
}
.mission-btn {
  padding: 6px 16px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  background: rgba(255, 255, 255, 0.1);
  color: #c3c5d7;
  border: none;
  cursor: pointer;
}
.mission-btn.active {
  background: rgba(181, 196, 255, 0.1);
  color: #b5c4ff;
}
</style>
