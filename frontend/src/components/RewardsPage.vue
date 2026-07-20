<template>
  <div class="rewards-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
    />

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat rewards..." />

      <template v-else>
        <section class="balance-card">
          <p class="balance-label">YOUR BALANCE</p>
          <div class="balance-value-row">
            <span class="material-symbols-outlined balance-icon">diamond</span>
            <span class="balance-value">{{ diamonds }}</span>
          </div>
          <div class="balance-hint">
            <span class="material-symbols-outlined">info</span>
            <span>Selesaikan misi harian untuk dapat diamond</span>
          </div>
        </section>

        <section class="chips-row">
          <button
            v-for="chip in categories"
            :key="chip.value"
            class="chip"
            :class="{ active: activeCategory === chip.value }"
            @click="activeCategory = chip.value"
          >
            {{ chip.label }}
          </button>
        </section>

        <section class="rewards-grid">
          <div v-for="reward in filteredRewards" :key="reward.id" class="reward-card">
            <div class="reward-icon" :class="`icon-${reward.color}`">
              <span class="material-symbols-outlined">{{ reward.icon }}</span>
            </div>
            <div class="reward-body">
              <h3>{{ reward.title }}</h3>
              <p>{{ reward.description }}</p>
              <div class="reward-footer">
                <div class="reward-cost">
                  <span class="material-symbols-outlined cost-icon">diamond</span>
                  <span>{{ reward.costDiamonds }}</span>
                </div>
                <button
                  class="redeem-btn"
                  :class="{ redeemed: redeemedIds.has(reward.id) }"
                  :disabled="!reward.inStock || diamonds < reward.costDiamonds || redeemingId === reward.id"
                  @click="handleRedeem(reward)"
                >
                  <span v-if="!reward.inStock">SOLD OUT</span>
                  <span v-else-if="redeemedIds.has(reward.id)">REDEEMED</span>
                  <span v-else-if="redeemingId === reward.id">...</span>
                  <span v-else>REDEEM</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        <p v-if="filteredRewards.length === 0" class="empty-text">
          Belum ada reward di kategori ini.
        </p>
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

const diamonds = ref(0)
const rewards = ref([])
const loading = ref(true)
const redeemingId = ref(null)
const redeemedIds = ref(new Set())

const categories = [
  { value: 'all', label: 'ALL' },
  { value: 'voucher', label: 'VOUCHERS' },
  { value: 'merch', label: 'MERCH' },
  { value: 'premium', label: 'PREMIUM' },
]
const activeCategory = ref('all')

const filteredRewards = computed(() =>
  activeCategory.value === 'all'
    ? rewards.value
    : rewards.value.filter((r) => r.category === activeCategory.value)
)

async function handleRedeem(reward) {
  if (redeemingId.value) return
  redeemingId.value = reward.id
  try {
    const { data } = await api.post(`/rewards/${reward.id}/redeem`)
    diamonds.value = data.remainingDiamonds
    redeemedIds.value.add(reward.id)
    redeemedIds.value = new Set(redeemedIds.value)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menukar reward')
  } finally {
    redeemingId.value = null
  }
}

async function loadRewards() {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }

  loading.value = true
  try {
    const { data } = await api.get('/rewards')
    diamonds.value = data.diamonds
    rewards.value = data.rewards
  } catch (err) {
    console.error('Failed to load rewards', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadRewards)
</script>

<style scoped>
.rewards-page {
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

/* Balance hero */
.balance-card {
  border-radius: 24px;
  padding: 24px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 20px rgba(79, 125, 255, 0.2);
}
.balance-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: rgba(181, 196, 255, 0.8);
  margin: 0 0 8px;
}
.balance-value-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.balance-icon {
  color: #b5c4ff;
  font-size: 28px;
  font-variation-settings: 'FILL' 1;
}
.balance-value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
}
.balance-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  color: #c3c5d7;
}
.balance-hint .material-symbols-outlined {
  font-size: 16px;
  color: #b5c4ff;
}

/* Chips */
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

/* Reward cards */
.rewards-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.reward-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.reward-icon {
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
.reward-body { flex: 1; min-width: 0; }
.reward-body h3 {
  font-size: 15px;
  font-weight: 700;
  margin: 0;
  color: #dce1fc;
}
.reward-body p {
  font-size: 12px;
  color: #c3c5d7;
  margin: 4px 0 0;
}
.reward-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}
.reward-cost {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 700;
  color: #b5c4ff;
}
.cost-icon {
  font-size: 16px;
  font-variation-settings: 'FILL' 1;
}
.redeem-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  border: none;
  cursor: pointer;
  background: #b5c4ff;
  color: #00297a;
  box-shadow: 0 4px 12px rgba(79, 125, 255, 0.3);
}
.redeem-btn:disabled {
  background: rgba(255, 255, 255, 0.05);
  color: #c3c5d7;
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}
.redeem-btn.redeemed {
  background: #34d399;
  color: #062e23;
  opacity: 1;
}

.empty-text {
  text-align: center;
  font-size: 13px;
  color: rgba(195, 197, 215, 0.6);
  padding: 24px 0;
}
</style>
