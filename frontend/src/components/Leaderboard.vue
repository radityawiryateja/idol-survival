<template>
  <div class="leaderboard-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
    />

    <main class="content">
      <section class="page-title">
        <h1>Global Ranking</h1>
        <p>Real-time survival statistics across all active sectors.</p>
      </section>

      <!-- Podium -->
      <section class="podium">
        <!-- Rank 2 -->
        <div class="podium-slot slot-2">
          <div class="podium-portrait float" style="animation-delay: 0.5s">
            <div class="ring ring-2">
              <img :src="podium[1]?.photo" :alt="podium[1]?.name" />
            </div>
            <span class="rank-tag tag-2">#2</span>
          </div>
          <div class="podium-base base-2">
            <span class="podium-name">{{ podium[1]?.name }}</span>
            <span class="podium-votes votes-2">{{ podium[1]?.votes }}</span>
          </div>
        </div>

        <!-- Rank 1 -->
        <div class="podium-slot slot-1">
          <div class="podium-portrait float">
            <span class="crown material-symbols-outlined">workspace_premium</span>
            <div class="ring ring-1">
              <img :src="podium[0]?.photo" :alt="podium[0]?.name" />
            </div>
            <span class="rank-tag tag-1">#1</span>
          </div>
          <div class="podium-base base-1">
            <span class="podium-name name-1">{{ podium[0]?.name }}</span>
            <span class="podium-votes votes-1">{{ podium[0]?.votes }}</span>
            <div class="trend">
              <span class="material-symbols-outlined trend-icon">trending_up</span>
              <span class="trend-value">{{ podium[0]?.trend }}</span>
            </div>
          </div>
        </div>

        <!-- Rank 3 -->
        <div class="podium-slot slot-3">
          <div class="podium-portrait float" style="animation-delay: 1s">
            <div class="ring ring-3">
              <img :src="podium[2]?.photo" :alt="podium[2]?.name" />
            </div>
            <span class="rank-tag tag-3">#3</span>
          </div>
          <div class="podium-base base-3">
            <span class="podium-name">{{ podium[2]?.name }}</span>
            <span class="podium-votes votes-3">{{ podium[2]?.votes }}</span>
          </div>
        </div>
      </section>

      <!-- Ranking list (4+) -->
      <section class="ranking-list">
        <div class="list-head">
          <span>RANKING DATA</span>
          <span>WEEKLY TREND</span>
        </div>

        <div v-for="entry in restOfRanking" :key="entry.id" class="ranking-row">
          <span class="row-position">{{ String(entry.rank).padStart(2, '0') }}</span>
          <div class="row-avatar">
            <img :src="entry.photo" :alt="entry.name" />
          </div>
          <div class="row-info">
            <h3>{{ entry.name }}</h3>
            <div class="row-meta">
              <span class="row-votes">{{ entry.votesFull }} Votes</span>
              <span class="row-trend" :class="trendClass(entry.trendDirection)">
                <span class="material-symbols-outlined trend-arrow">
                  {{ trendIcon(entry.trendDirection) }}
                </span>
                {{ entry.trendPercent }}%
              </span>
            </div>
          </div>
          <div class="row-sparkline">
            <svg viewBox="0 0 100 40" :class="trendClass(entry.trendDirection)">
              <path :d="entry.sparkline" fill="none" stroke="currentColor" stroke-width="2" />
            </svg>
          </div>
        </div>
      </section>

      <!-- Weekly prestige meter -->
      <section class="prestige-card">
        <div class="prestige-head">
          <h4>Weekly Prestige Cap</h4>
          <span class="prestige-percent">{{ prestige.percent }}%</span>
        </div>
        <div class="prestige-track">
          <div class="prestige-fill" :style="{ width: prestige.percent + '%' }"></div>
        </div>
        <p class="prestige-note">{{ prestige.note }}</p>
      </section>
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

const profile = ref({ name: 'Producer', tier: 'DIAMOND SUPPORTER', level: 1, avatarUrl: '' })

// ranking = full ordered list from the backend; podium = first 3, restOfRanking = rank 4+
const ranking = ref([])
const prestige = ref({ percent: 0, note: '' })

const podium = computed(() => ranking.value.slice(0, 3))
const restOfRanking = computed(() => ranking.value.slice(3))

function trendClass(direction) {
  if (direction === 'up') return 'trend-up'
  if (direction === 'down') return 'trend-down'
  return 'trend-flat'
}

function trendIcon(direction) {
  if (direction === 'up') return 'arrow_drop_up'
  if (direction === 'down') return 'arrow_drop_down'
  return 'remove'
}

async function loadLeaderboard() {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }

  try {
    const { data } = await api.get('/leaderboard')
    ranking.value = data.ranking
    prestige.value = data.prestige
  } catch (err) {
    console.error('Failed to load leaderboard', err)
  }
}

onMounted(loadLeaderboard)
</script>

<style scoped>
.leaderboard-page {
  min-height: 100dvh;
  padding-bottom: 128px;
  background: #0d1226;
  color: #dce1fc;
  overflow-x: hidden;
}
.content {
  max-width: 480px;
  margin: 0 auto;
  padding: 96px 20px 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-title h1 {
  font-size: 34px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
}
.page-title p {
  font-size: 14px;
  color: rgba(220, 225, 252, 0.8);
  margin: 0;
}

/* Podium */
.podium {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  align-items: end;
  height: 288px;
}
.podium-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.podium-portrait {
  position: relative;
  margin-bottom: 16px;
}
.float {
  animation: float 4s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.crown {
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  color: #b5c4ff;
  font-size: 28px;
}
.ring {
  border-radius: 50%;
  padding: 4px;
}
.ring img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}
.ring-1 {
  width: 96px;
  height: 96px;
  border: 4px solid #b5c4ff;
  box-shadow: 0 0 24px rgba(79, 125, 255, 0.4);
}
.ring-2 {
  width: 80px;
  height: 80px;
  border: 2px solid rgba(197, 192, 255, 0.4);
}
.ring-3 {
  width: 80px;
  height: 80px;
  border: 2px solid rgba(126, 141, 210, 0.4);
}
.rank-tag {
  position: absolute;
  bottom: -8px;
  right: 0;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
.tag-1 { background: #b5c4ff; color: #00297a; font-size: 12px; padding: 4px 12px; }
.tag-2 { background: #c5c0ff; color: #2600a1; }
.tag-3 { background: #7e8dd2; color: #122463; }
.podium-base {
  width: 100%;
  border-radius: 16px 16px 0 0;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.base-1 { height: 160px; box-shadow: 0 -10px 40px rgba(79, 125, 255, 0.1); }
.base-2 { height: 96px; }
.base-3 { height: 80px; }
.podium-name {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  max-width: 90%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.name-1 { font-size: 18px; margin-bottom: 4px; }
.podium-votes { font-size: 11px; font-weight: 700; }
.votes-1 { font-size: 24px; font-weight: 600; }
.votes-2 { color: #c5c0ff; }
.votes-3 { color: #7e8dd2; }
.votes-1 { color: #b5c4ff; }
.trend {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
}
.trend-icon { font-size: 14px; color: #b5c4ff; }
.trend-value { font-size: 10px; font-weight: 700; color: #b5c4ff; }

/* Ranking list */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.list-head {
  display: flex;
  justify-content: space-between;
  padding: 0 16px;
  margin-bottom: 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
}
.ranking-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.row-position {
  font-size: 18px;
  font-weight: 600;
  color: #c3c5d7;
  width: 24px;
  flex-shrink: 0;
}
.row-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}
.row-avatar img { width: 100%; height: 100%; object-fit: cover; }
.row-info { flex: 1; min-width: 0; }
.row-info h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #dce1fc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.row-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}
.row-votes {
  font-size: 12px;
  color: #c3c5d7;
}
.row-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
}
.trend-arrow { font-size: 12px; }
.trend-up { color: #b5c4ff; }
.trend-down { color: #ffb4ab; }
.trend-flat { color: #c3c5d7; }
.row-sparkline {
  width: 64px;
  height: 32px;
  opacity: 0.6;
  flex-shrink: 0;
}
.row-sparkline svg {
  width: 100%;
  height: 100%;
}

/* Weekly prestige */
.prestige-card {
  border-radius: 24px;
  padding: 24px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.prestige-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.prestige-head h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #dce1fc;
}
.prestige-percent {
  font-size: 11px;
  font-weight: 700;
  color: #b5c4ff;
}
.prestige-track {
  height: 4px;
  background: #0d1226;
  border-radius: 999px;
  overflow: hidden;
}
.prestige-fill {
  height: 100%;
  background: linear-gradient(90deg, #3c24c5, #b5c4ff);
  box-shadow: 0 0 12px rgba(79, 125, 255, 0.4);
}
.prestige-note {
  font-size: 12px;
  color: rgba(195, 197, 215, 0.6);
  margin: 8px 0 0;
}
</style>
