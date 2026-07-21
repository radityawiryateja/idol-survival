<template>
  <div class="idols-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
      :frame-style="profile.frameStyle"
      :frame-asset-url="profile.frameAssetUrl"
    />

    <main class="content">
      <!-- Search & filters -->
      <section class="filters">
        <div class="search-row">
          <div class="search-box">
            <span class="material-symbols-outlined search-icon">search</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search contestants..."
              class="search-input"
            />
          </div>
          <button class="tune-btn" aria-label="Filters">
            <span class="material-symbols-outlined">tune</span>
          </button>
        </div>

        <div class="season-row">
          <div class="season-select">
            <span class="season-label">SEASON</span>
            <select v-model="selectedSeason" class="season-dropdown">
              <option v-for="s in seasons" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <span class="total-count">{{ totalContestants }} CONTESTANTS</span>
        </div>

        <div class="chips-row">
          <button
            v-for="chip in chips"
            :key="chip"
            class="chip"
            :class="{ active: activeChip === chip }"
            @click="activeChip = chip"
          >
            {{ chip }}
          </button>
        </div>
      </section>

      <LoadingSpinner v-if="loading" label="Memuat idols..." />

      <template v-else>
        <!-- Top 3 premium cards -->
        <section class="idol-list">
          <div
            v-for="idol in topThree"
            :key="idol.id"
            class="idol-card premium"
            :class="`premium-${idol.rank}`"
          >
            <div class="card-row">
              <router-link :to="`/idols/${idol.id}/card`" class="portrait">
                <img :src="idol.photo || idol.photo_url" :alt="idol.name" />
                <span class="rank-badge" :class="`rank-${idol.rank}`">RANK {{ idol.rank }}</span>
              </router-link>
              <div class="info">
                <div class="info-top">
                  <div>
                    <h3 class="idol-name">{{ idol.name }}</h3>
                    <p class="agency" :class="`agency-${idol.rank}`">{{ idol.agency }}</p>
                    <router-link :to="`/idols/${idol.id}/card`" class="idcard-link">View ID Card →</router-link>
                  </div>
                  <button
                    class="fav-btn"
                    :class="{ active: idol.favorited }"
                    @click="toggleFavorite(idol)"
                    aria-label="Toggle favorite"
                  >
                    <span class="material-symbols-outlined">favorite</span>
                  </button>
                </div>

                <div class="metrics">
                  <div class="metric">
                    <p class="metric-label">TOTAL VOTES</p>
                    <p class="metric-value" :class="`text-${idol.rank}`">{{ idol.votes }}</p>
                  </div>
                  <div class="divider"></div>
                  <div class="metric">
                    <p class="metric-label">FOLLOWERS</p>
                    <p class="metric-value">{{ idol.followers }}</p>
                  </div>
                </div>

                <div class="sparkline-row">
                  <svg class="sparkline" viewBox="0 0 100 40">
                    <path :d="idol.sparkline" fill="none" :stroke="rankColor(idol.rank)" stroke-width="2" />
                  </svg>
                  <div class="popularity">
                    <span class="popularity-label">POPULARITY</span>
                    <span class="popularity-value" :class="`text-${idol.rank}`">{{ idol.popularity }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <button class="vote-btn" :class="`vote-${idol.rank}`" @click="openVoteModal(idol)">
              Cast Vote
            </button>
          </div>
        </section>

        <!-- Remaining ranks as compact list items -->
        <section class="idol-list-compact">
          <div v-for="idol in restOfList" :key="idol.id" class="idol-row">
            <span class="row-rank">{{ String(idol.rank).padStart(2, '0') }}</span>
            <router-link :to="`/idols/${idol.id}/card`" class="row-avatar">
              <img :src="idol.photo || idol.photo_url" :alt="idol.name" />
            </router-link>
            <div class="row-info">
              <h4>{{ idol.name }}</h4>
              <p>{{ idol.agency }}</p>
            </div>
            <div class="row-votes">
              <p class="row-votes-value">{{ idol.votes }}</p>
              <p class="row-votes-label">VOTES</p>
            </div>
            <button class="row-vote-btn" @click="openVoteModal(idol)" aria-label="Vote">
              <span class="material-symbols-outlined">how_to_reg</span>
            </button>
          </div>
        </section>
      </template>
    </main>

    <BottomNav />
    <VoteModal
      v-if="activeVoteIdol"
      :idol="activeVoteIdol"
      :balance="walletBalance"
      @close="activeVoteIdol = null"
      @confirm="onConfirmVote"
      />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../lib/api'
import { getUser, getFrame } from '../lib/auth'
import TopAppBar from './TopAppBar.vue'
import BottomNav from './BottomNav.vue'
import VoteModal from './VoteModal.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const profile = ref({ 
  name: 'Producer', 
  tier: 'DIAMOND SUPPORTER', 
  level: 1, 
  avatarUrl: '',
  frameStyle: 'none',
  frameAssetUrl: ''
})

const searchQuery = ref('')
const seasons = ['S04: FINAL GATE', 'S03: ORIGINS']
const selectedSeason = ref(seasons[0])
const chips = ['ALL', 'TOP RANK', 'POPULAR', 'ROOKIES', 'FAVORITES']
const activeChip = ref('ALL')
const totalContestants = ref(0)
const walletBalance = ref(0)
const activeVoteIdol = ref(null)
const loading = ref(true)

const idols = ref([])

const topThree = computed(() => idols.value.filter((i) => i.rank <= 3))
const restOfList = computed(() => idols.value.filter((i) => i.rank > 3))

function rankColor(rank) {
  return { 1: '#4F7DFF', 2: '#C5C0FF', 3: '#B8C4FF' }[rank] || '#B8C4FF'
}

async function toggleFavorite(idol) {
  idol.favorited = !idol.favorited
  try {
    await api.post(`/idols/${idol.id}/favorite`, { favorited: idol.favorited })
  } catch (err) {
    idol.favorited = !idol.favorited // revert on failure
    console.error('Failed to update favorite', err)
  }
}

function openVoteModal(idol) {
  activeVoteIdol.value = idol
}

async function onConfirmVote(quantity) {
  const idol = activeVoteIdol.value
  try {
    const { data } = await api.post(`/idols/${idol.id}/vote`, { quantity })
    walletBalance.value = data.remainingTickets
    idol.votesRaw += quantity
    idol.votes = formatVotes(idol.votesRaw)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal vote')
  } finally {
    activeVoteIdol.value = null
  }
}

function formatVotes(n) {
  return n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n.toLocaleString()
}

async function loadIdols() {
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
    const { data } = await api.get('/idols', {
      params: { season: selectedSeason.value, filter: activeChip.value, q: searchQuery.value },
    })
    idols.value = data.idols
    totalContestants.value = data.total
  } catch (err) {
    console.error('Failed to load idols', err)
  } finally {
    loading.value = false
  }
  try {
    const profileRes = await api.get('/profile/me')
      walletBalance.value = profileRes.data.voteTickets
  } catch (err) {
    console.error('Failed to load wallet balance', err)
  }
}

onMounted(loadIdols)
</script>

<style scoped>
.idols-page {
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

/* Filters */
.filters {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.search-row {
  display: flex;
  gap: 8px;
}
.search-box {
  position: relative;
  flex: 1;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(195, 197, 215, 0.5);
  font-size: 20px;
}
.search-input {
  width: 100%;
  background: #070d20;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px 12px 40px;
  color: #dce1fc;
  font-size: 14px;
}
.search-input::placeholder {
  color: rgba(195, 197, 215, 0.4);
}
.search-input:focus {
  outline: none;
  border-color: #4f7dff;
}
.tune-btn {
  background: #23293d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  color: #b5c4ff;
  display: flex;
  align-items: center;
  cursor: pointer;
}
.season-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.season-select {
  display: flex;
  align-items: center;
  gap: 8px;
}
.season-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #c3c5d7;
}
.season-dropdown {
  background: transparent;
  color: #b5c4ff;
  font-weight: 700;
  font-size: 14px;
  border: none;
  cursor: pointer;
}
.total-count {
  font-size: 11px;
  letter-spacing: 0.05em;
  color: rgba(195, 197, 215, 0.6);
}
.chips-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
}
.chip {
  padding: 8px 16px;
  border-radius: 999px;
  background: #23293d;
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: #c3c5d7;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  white-space: nowrap;
  cursor: pointer;
}
.chip.active {
  background: #b5c4ff;
  color: #00297a;
  border-color: transparent;
  box-shadow: 0 0 12px rgba(79, 125, 255, 0.3);
}

/* Premium idol cards */
.idol-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.idol-card {
  border-radius: 24px;
  padding: 16px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 2px solid transparent;
}
.premium-1 { border-image: linear-gradient(to bottom right, #4F7DFF, #3C24C5) 1; }
.premium-2 { border-image: linear-gradient(to bottom right, #C5C0FF, #7E8DD2) 1; }
.premium-3 { border-image: linear-gradient(to bottom right, #B8C4FF, #434654) 1; }
.card-row {
  display: flex;
  gap: 16px;
}
.portrait {
  position: relative;
  width: 128px;
  height: 160px;
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
}
.portrait img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.rank-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}
.rank-1 { background: #b5c4ff; color: #00297a; }
.rank-2 { background: #c5c0ff; color: #2600a1; }
.rank-3 { background: #7e8dd2; color: #122463; }
.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4px 0;
}
.idcard-link {
  font-size: 11px;
  color: #b5c4ff;
  text-decoration: none;
  margin-top: 4px;
  display: inline-block;
}
.info-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.idol-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #dce1fc;
}
.agency {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin: 2px 0 0;
}
.agency-1 { color: #b5c4ff; }
.agency-2 { color: #c5c0ff; }
.agency-3 { color: #b8c4ff; }
.fav-btn {
  background: none;
  border: none;
  color: rgba(195, 197, 215, 0.4);
  cursor: pointer;
  font-size: 0;
}
.fav-btn .material-symbols-outlined { font-variation-settings: 'FILL' 0; }
.fav-btn.active { color: #ffb4ab; }
.fav-btn.active .material-symbols-outlined { font-variation-settings: 'FILL' 1; }
.metrics {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}
.metric { text-align: center; }
.metric-label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(195, 197, 215, 0.6);
  margin: 0;
}
.metric-value {
  font-size: 14px;
  font-weight: 700;
  margin: 2px 0 0;
}
.divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
}
.text-1 { color: #b5c4ff; }
.text-2 { color: #c5c0ff; }
.text-3 { color: #7e8dd2; }
.sparkline-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: 8px;
}
.sparkline { width: 80px; height: 32px; }
.popularity { text-align: right; }
.popularity-label {
  font-size: 10px;
  font-weight: 700;
  color: rgba(195, 197, 215, 0.6);
  display: block;
}
.popularity-value {
  font-size: 14px;
  font-weight: 700;
}
.vote-btn {
  width: 100%;
  margin-top: 16px;
  padding: 12px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border: none;
  cursor: pointer;
}
.vote-1 { background: linear-gradient(90deg, #4f7dff, #3d66d6); color: #00297a; box-shadow: 0 0 12px rgba(79, 125, 255, 0.4); }
.vote-2 { background: #191f32; color: #c5c0ff; border: 1px solid rgba(197, 192, 255, 0.3); }
.vote-3 { background: #191f32; color: #b8c4ff; border: 1px solid rgba(184, 196, 255, 0.3); }

/* Compact rows for rank 4+ */
.idol-list-compact {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.idol-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.row-rank {
  font-size: 12px;
  color: rgba(195, 197, 215, 0.4);
  width: 16px;
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
.row-info h4 {
  font-size: 14px;
  font-weight: 700;
  margin: 0;
  color: #dce1fc;
}
.row-info p {
  font-size: 10px;
  color: rgba(195, 197, 215, 0.6);
  margin: 2px 0 0;
}
.row-votes { text-align: right; margin-right: 4px; }
.row-votes-value {
  font-size: 11px;
  font-weight: 700;
  color: #b5c4ff;
  margin: 0;
}
.row-votes-label {
  font-size: 8px;
  color: rgba(195, 197, 215, 0.4);
  margin: 0;
}
.row-vote-btn {
  background: rgba(181, 196, 255, 0.1);
  color: #b5c4ff;
  border: none;
  border-radius: 8px;
  padding: 8px;
  display: flex;
  cursor: pointer;
}
</style>
