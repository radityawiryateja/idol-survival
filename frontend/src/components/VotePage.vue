<template>
  <div class="vote-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
      :frame-style="profile.frameStyle"
      :frame-asset-url="profile.frameAssetUrl"
    />

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat vote hub..." />

      <template v-else>
        <!-- Wallet + streak -->
        <section class="wallet-card">
          <div class="wallet-row">
            <div class="wallet-stat">
              <span class="material-symbols-outlined wallet-icon">confirmation_number</span>
              <div>
                <p class="wallet-value">{{ voteTickets }}</p>
                <p class="wallet-label">VOTE TICKETS</p>
              </div>
            </div>
            <div class="wallet-divider"></div>
            <div class="wallet-stat">
              <span class="material-symbols-outlined wallet-icon streak">local_fire_department</span>
              <div>
                <p class="wallet-value">{{ streakDays }}D</p>
                <p class="wallet-label">VOTE STREAK</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Spotlight idol -->
        <section v-if="spotlight" class="spotlight-card">
          <span class="spotlight-tag">TOP RANK — VOTE NOW</span>
          <div class="spotlight-row">
            <img :src="spotlight.photo" :alt="spotlight.name" class="spotlight-photo" />
            <div class="spotlight-info">
              <h2>{{ spotlight.name }}</h2>
              <p>{{ spotlight.agency }}</p>
              <div class="spotlight-votes">
                <span>{{ spotlight.votes }} votes</span>
                <span class="trend" :class="`trend-${spotlight.trendDirection}`">
                  <span class="material-symbols-outlined">
                    {{ spotlight.trendDirection === 'up' ? 'trending_up' : 'trending_flat' }}
                  </span>
                  {{ spotlight.trendPercent }}%
                </span>
              </div>
            </div>
          </div>
          <button class="spotlight-vote-btn" @click="openVoteModal(spotlight)">
            Cast Vote Sekarang
          </button>
        </section>

        <!-- Quick vote list -->
        <section class="quick-list">
          <h3>QUICK VOTE</h3>
          <div v-for="idol in quickList" :key="idol.id" class="quick-row">
            <img :src="idol.photo" :alt="idol.name" class="quick-avatar" />
            <div class="quick-info">
              <h4>{{ idol.name }}</h4>
              <p>{{ idol.votes }} votes</p>
            </div>
            <button
              class="quick-vote-btn"
              :disabled="votingId === idol.id || voteTickets < 1"
              @click="handleQuickVote(idol)"
            >
              <span v-if="votingId === idol.id">...</span>
              <span v-else class="material-symbols-outlined">add</span>
            </button>
          </div>
          <p v-if="quickList.length === 0" class="empty-text">Belum ada idol lain untuk divote.</p>
        </section>
      </template>
    </main>

    <BottomNav />
    <VoteModal
      v-if="activeVoteIdol"
      :idol="activeVoteIdol"
      :balance="voteTickets"
      @close="activeVoteIdol = null"
      @confirm="onConfirmVote"
    />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../lib/api'
import { getUser, getFrame } from '../lib/auth'
import TopAppBar from './TopAppBar.vue'
import BottomNav from './BottomNav.vue'
import LoadingSpinner from './LoadingSpinner.vue'
import VoteModal from './VoteModal.vue'

const profile = ref({ 
  name: 'Producer', 
  tier: 'DIAMOND SUPPORTER', 
  level: 1, 
  avatarUrl: '',
  frameStyle: 'none',
  frameAssetUrl: ''
})

const loading = ref(true)
const voteTickets = ref(0)
const streakDays = ref(0)
const spotlight = ref(null)
const quickList = ref([])

const activeVoteIdol = ref(null)
const votingId = ref(null)

function openVoteModal(idol) {
  // VoteModal butuh field `id` dan `name` — spotlight & quick-list row
  // sudah cocok bentuknya.
  activeVoteIdol.value = idol
}

async function onConfirmVote(quantity) {
  const idol = activeVoteIdol.value
  try {
    const { data } = await api.post(`/idols/${idol.id}/vote`, { quantity })
    voteTickets.value = data.remainingTickets
    idol.votesRaw += quantity
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal vote')
  } finally {
    activeVoteIdol.value = null
  }
}

// Tombol "+" di list ringkas -- vote 1 tiket langsung tanpa buka modal.
async function handleQuickVote(idol) {
  if (votingId.value || voteTickets.value < 1) return
  votingId.value = idol.id
  try {
    const { data } = await api.post(`/idols/${idol.id}/vote`, { quantity: 1 })
    voteTickets.value = data.remainingTickets
    idol.votesRaw += 1
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal vote')
  } finally {
    votingId.value = null
  }
}

async function loadVoteHub() {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }

  const cachedFrame = getFrame()
  if (cachedFrame) {
    profile.value.frameStyle = cachedFrame.style
    profile.value.frameAssetUrl = cachedFrame.assetUrl
  }

  loading.value = true
  try {
    const { data } = await api.get('/vote/summary')
    voteTickets.value = data.voteTickets
    streakDays.value = data.streakDays
    spotlight.value = data.spotlight
    quickList.value = data.quickList
  } catch (err) {
    console.error('Failed to load vote hub', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadVoteHub)
</script>

<style scoped>
.vote-page {
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

.wallet-card {
  border-radius: 24px;
  padding: 20px 24px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 20px rgba(79, 125, 255, 0.2);
}
.wallet-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}
.wallet-stat {
  display: flex;
  align-items: center;
  gap: 10px;
}
.wallet-icon { color: #b5c4ff; font-size: 24px; }
.wallet-icon.streak { color: #fbbf24; }
.wallet-value { font-size: 20px; font-weight: 700; color: #fff; margin: 0; }
.wallet-label { font-size: 10px; font-weight: 700; letter-spacing: 0.05em; color: #c3c5d7; margin: 0; }
.wallet-divider { width: 1px; height: 32px; background: rgba(255, 255, 255, 0.1); }

.spotlight-card {
  border-radius: 24px;
  padding: 20px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(181, 196, 255, 0.3);
  box-shadow: 0 0 24px rgba(79, 125, 255, 0.25);
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.spotlight-tag {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #b5c4ff;
}
.spotlight-row {
  display: flex;
  gap: 16px;
  align-items: center;
}
.spotlight-photo {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  object-fit: cover;
  border: 2px solid rgba(181, 196, 255, 0.4);
}
.spotlight-info h2 { font-size: 18px; font-weight: 700; margin: 0; color: #fff; }
.spotlight-info p { font-size: 12px; color: #c3c5d7; margin: 2px 0 8px; }
.spotlight-votes { display: flex; align-items: center; gap: 10px; font-size: 12px; font-weight: 700; color: #dce1fc; }
.trend { display: flex; align-items: center; gap: 2px; }
.trend .material-symbols-outlined { font-size: 14px; }
.trend-up { color: #b5c4ff; }
.trend-flat { color: #c3c5d7; }
.spotlight-vote-btn {
  padding: 14px;
  border-radius: 12px;
  background: linear-gradient(90deg, #4f7dff, #3d66d6);
  color: #00297a;
  font-weight: 700;
  border: none;
  cursor: pointer;
}

.quick-list { display: flex; flex-direction: column; gap: 8px; }
.quick-list h3 {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
  margin: 0 0 4px;
}
.quick-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.quick-avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; }
.quick-info { flex: 1; min-width: 0; }
.quick-info h4 { font-size: 13px; font-weight: 700; margin: 0; color: #dce1fc; }
.quick-info p { font-size: 11px; color: #c3c5d7; margin: 0; }
.quick-vote-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: rgba(181, 196, 255, 0.15);
  color: #b5c4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.quick-vote-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.empty-text {
  text-align: center;
  font-size: 13px;
  color: rgba(195, 197, 215, 0.6);
  padding: 16px 0;
}
</style>
