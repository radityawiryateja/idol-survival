<template>
  <div class="events-page">
    <!-- LIST VIEW -->
    <template v-if="!activeEvent">
      <TopAppBar
        :name="profile.name"
        :tier="profile.tier"
        :level="profile.level"
        :avatar-url="profile.avatarUrl"
      />

      <main class="content">
        <section class="page-title">
          <h1>Events</h1>
          <p>Ikuti event spesial dan klaim reward-nya sebelum waktu habis.</p>
        </section>

        <LoadingSpinner v-if="loading" label="Memuat event..." />

        <template v-else>
          <section class="event-list">
            <button
              v-for="event in events"
              :key="event.id"
              class="event-card"
              :class="[`accent-${event.color}`, { ended: event.status === 'ended' }]"
              :style="bannerStyle(event)"
              @click="openEvent(event)"
            >
              <div class="card-overlay"></div>
              <div class="card-top">
                <span class="status-badge" :class="`status-${event.status}`">
                  {{ statusLabel(event.status) }}
                </span>
                <span class="countdown-badge">{{ event.countdown }}</span>
              </div>

              <div class="card-body">
                <p class="event-subtitle">{{ event.subtitle }}</p>
                <h2 class="event-title">{{ event.title }}</h2>

                <div class="progress-row">
                  <div class="progress-track">
                    <div
                      class="progress-fill"
                      :class="`fill-${event.color}`"
                      :style="{ width: overallPercent(event) + '%' }"
                    ></div>
                  </div>
                  <span class="progress-text">
                    {{ event.progress }} {{ event.progressLabel }}
                  </span>
                </div>
              </div>
            </button>
          </section>

          <p v-if="events.length === 0" class="empty-text">Belum ada event yang berjalan saat ini.</p>
        </template>
      </main>

      <BottomNav />
    </template>

    <!-- DETAIL VIEW -->
    <template v-else>
      <header class="detail-top-bar">
        <button class="back-btn" @click="closeEvent" aria-label="Back">
          <span class="material-symbols-outlined">arrow_back_ios_new</span>
        </button>
        <h2 class="detail-title">{{ activeEvent.title }}</h2>
        <div class="spacer"></div>
      </header>

      <main class="detail-content">
        <LoadingSpinner v-if="loadingDetail" label="Memuat detail event..." />

        <template v-else-if="detail">
          <section class="detail-banner" :style="bannerStyle(detail)">
            <div class="banner-overlay"></div>
            <div class="banner-info">
              <span class="status-badge" :class="`status-${detail.status}`">
                {{ statusLabel(detail.status) }}
              </span>
              <h1>{{ detail.title }}</h1>
              <p>{{ detail.subtitle }}</p>
              <span class="countdown-pill">{{ detail.countdown }}</span>
            </div>
          </section>

          <p class="detail-description">{{ detail.description }}</p>

          <section class="progress-summary" :class="`accent-${detail.color}`">
            <div class="summary-row">
              <span>Progress Kamu</span>
              <span class="summary-value">{{ detail.progress }} {{ detail.progressLabel }}</span>
            </div>
            <div class="summary-row small">
              <span>{{ detail.claimedMilestones }} / {{ detail.totalMilestones }} Reward Diklaim</span>
            </div>
          </section>

          <section class="milestones">
            <h3>Reward Milestones</h3>

            <div
              v-for="milestone in detail.milestones"
              :key="milestone.id"
              class="milestone-card"
              :class="{ claimed: milestone.claimed, claimable: milestone.claimable }"
            >
              <div class="milestone-icon" :class="`icon-${detail.color}`">
                <span class="material-symbols-outlined">{{ milestone.icon }}</span>
              </div>
              <div class="milestone-body">
                <div class="milestone-top">
                  <h4>{{ milestone.title }}</h4>
                  <div class="milestone-rewards">
                    <span v-if="milestone.rewardDiamonds" class="reward-chip">
                      <span class="material-symbols-outlined">diamond</span>{{ milestone.rewardDiamonds }}
                    </span>
                    <span v-if="milestone.rewardVoteTickets" class="reward-chip">
                      <span class="material-symbols-outlined">confirmation_number</span>{{ milestone.rewardVoteTickets }}
                    </span>
                  </div>
                </div>
                <div class="milestone-progress-track">
                  <div
                    class="milestone-progress-fill"
                    :class="`fill-${detail.color}`"
                    :style="{ width: milestone.progressPercent + '%' }"
                  ></div>
                </div>
                <p class="milestone-status">
                  {{ detail.progress }} / {{ milestone.targetCount }} {{ detail.progressLabel }}
                </p>
              </div>
              <button
                class="claim-btn"
                :class="{ ready: milestone.claimable, done: milestone.claimed }"
                :disabled="!milestone.claimable || claimingId === milestone.id"
                @click="handleClaim(milestone)"
              >
                <span v-if="milestone.claimed">DONE</span>
                <span v-else-if="claimingId === milestone.id">...</span>
                <span v-else-if="milestone.claimable">CLAIM</span>
                <span v-else>LOCKED</span>
              </button>
            </div>
          </section>
        </template>
      </main>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../lib/api'
import { getUser } from '../lib/auth'
import TopAppBar from './TopAppBar.vue'
import BottomNav from './BottomNav.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const profile = ref({ name: 'Producer', tier: 'DIAMOND SUPPORTER', level: 1, avatarUrl: '' })

const events = ref([])
const loading = ref(true)

const activeEvent = ref(null)
const detail = ref(null)
const loadingDetail = ref(false)
const claimingId = ref(null)

function statusLabel(status) {
  if (status === 'active') return 'LIVE NOW'
  if (status === 'upcoming') return 'UPCOMING'
  return 'ENDED'
}

function bannerStyle(event) {
  return {
    backgroundImage: event.bannerImage ? `url(${event.bannerImage})` : 'none',
  }
}

// Progress terhadap milestone terakhir, dipakai buat progress bar ringkas di kartu list.
function overallPercent(event) {
  if (!event.finalTarget) return 0
  return Math.min(100, Math.round((event.progress / event.finalTarget) * 100))
}

async function loadEvents() {
  loading.value = true
  try {
    const { data } = await api.get('/events')
    events.value = data.events
  } catch (err) {
    console.error('Failed to load events', err)
  } finally {
    loading.value = false
  }
}

async function openEvent(event) {
  activeEvent.value = event
  loadingDetail.value = true
  try {
    const { data } = await api.get(`/events/${event.id}`)
    detail.value = data
  } catch (err) {
    console.error('Failed to load event detail', err)
  } finally {
    loadingDetail.value = false
  }
}

function closeEvent() {
  activeEvent.value = null
  detail.value = null
  loadEvents() // refresh progress ringkas di list setelah balik dari detail
}

async function handleClaim(milestone) {
  if (claimingId.value) return
  claimingId.value = milestone.id
  try {
    await api.post(`/events/${activeEvent.value.id}/milestones/${milestone.id}/claim`)
    milestone.claimed = true
    milestone.claimable = false
    detail.value.claimedMilestones += 1
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal klaim reward event')
  } finally {
    claimingId.value = null
  }
}

onMounted(() => {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }
  loadEvents()
})
</script>

<style scoped>
.events-page {
  min-height: 100dvh;
  padding-bottom: 128px;
  background: #0d1226;
  color: #dce1fc;
}

/* List view */
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

.event-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.event-card {
  position: relative;
  width: 100%;
  min-height: 180px;
  border-radius: 24px;
  overflow: hidden;
  background-color: #191f32;
  background-size: cover;
  background-position: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0;
  cursor: pointer;
  text-align: left;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.event-card.ended {
  opacity: 0.55;
}
.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, #0a0e1f 10%, rgba(10, 14, 31, 0.4) 60%, rgba(10, 14, 31, 0.1));
}
.card-top {
  position: relative;
  display: flex;
  justify-content: space-between;
  padding: 16px;
}
.card-body {
  position: relative;
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.event-subtitle {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #b5c4ff;
  margin: 0;
}
.event-title {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px;
}

.status-badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 4px 10px;
  border-radius: 999px;
  height: fit-content;
}
.status-active { background: rgba(181, 196, 255, 0.9); color: #00297a; }
.status-upcoming { background: rgba(255, 255, 255, 0.15); color: #dce1fc; }
.status-ended { background: rgba(255, 255, 255, 0.08); color: rgba(220, 225, 252, 0.6); }
.countdown-badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #dce1fc;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 10px;
  border-radius: 999px;
  backdrop-filter: blur(8px);
}

.progress-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.progress-track {
  flex: 1;
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
  overflow: hidden;
}
.progress-fill { height: 100%; }
.fill-primary { background: linear-gradient(90deg, #b5c4ff, #4f7dff); }
.fill-secondary { background: linear-gradient(90deg, #c5c0ff, #3c24c5); }
.fill-tertiary { background: linear-gradient(90deg, #b8c4ff, #7e8dd2); }
.progress-text {
  font-size: 11px;
  font-weight: 700;
  color: #dce1fc;
  white-space: nowrap;
}

.empty-text {
  text-align: center;
  font-size: 13px;
  color: rgba(195, 197, 215, 0.6);
  padding: 24px 0;
}

/* Detail view */
.detail-top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 50;
  background: rgba(13, 18, 38, 0.8);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 12px;
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
.back-btn:hover { background: rgba(255, 255, 255, 0.05); }
.detail-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}
.spacer { width: 40px; }

.detail-content {
  max-width: 480px;
  margin: 0 auto;
  padding: 80px 20px 128px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-banner {
  position: relative;
  height: 200px;
  border-radius: 24px;
  overflow: hidden;
  background-color: #191f32;
  background-size: cover;
  background-position: center;
}
.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, #0d1226, rgba(13, 18, 38, 0.3));
}
.banner-info {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 20px;
  gap: 6px;
}
.banner-info h1 {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}
.banner-info p {
  font-size: 13px;
  color: #c3c5d7;
  margin: 0;
}
.countdown-pill {
  align-self: flex-start;
  margin-top: 4px;
  font-size: 11px;
  font-weight: 700;
  color: #dce1fc;
  background: rgba(0, 0, 0, 0.4);
  padding: 4px 10px;
  border-radius: 999px;
}

.detail-description {
  font-size: 13px;
  line-height: 1.6;
  color: #c3c5d7;
  margin: 0;
}

.progress-summary {
  border-radius: 20px;
  padding: 20px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 700;
  color: #dce1fc;
}
.summary-row.small {
  font-size: 12px;
  font-weight: 600;
  color: #c3c5d7;
}
.accent-primary .summary-value { color: #b5c4ff; }
.accent-secondary .summary-value { color: #c5c0ff; }
.accent-tertiary .summary-value { color: #b8c4ff; }

.milestones {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.milestones h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #fff;
}
.milestone-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.milestone-card.claimable {
  border-color: rgba(181, 196, 255, 0.4);
  box-shadow: 0 0 12px rgba(79, 125, 255, 0.15);
}
.milestone-card.claimed {
  opacity: 0.6;
}
.milestone-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-primary { background: rgba(181, 196, 255, 0.1); color: #b5c4ff; }
.icon-secondary { background: rgba(197, 192, 255, 0.2); color: #c5c0ff; }
.icon-tertiary { background: rgba(126, 141, 210, 0.2); color: #b8c4ff; }
.milestone-body { flex: 1; min-width: 0; }
.milestone-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.milestone-top h4 {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
  color: #dce1fc;
}
.milestone-rewards {
  display: flex;
  gap: 8px;
}
.reward-chip {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 11px;
  font-weight: 700;
  color: #b5c4ff;
}
.reward-chip .material-symbols-outlined {
  font-size: 14px;
}
.milestone-progress-track {
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  overflow: hidden;
  margin-bottom: 6px;
}
.milestone-progress-fill { height: 100%; }
.milestone-status {
  font-size: 11px;
  color: #c3c5d7;
  margin: 0;
}
.claim-btn {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(195, 197, 215, 0.5);
}
.claim-btn.ready {
  background: #b5c4ff;
  color: #00297a;
  box-shadow: 0 4px 12px rgba(79, 125, 255, 0.3);
}
.claim-btn.done {
  background: #34d399;
  color: #062e23;
}
.claim-btn:disabled:not(.done) {
  cursor: not-allowed;
}
</style>
