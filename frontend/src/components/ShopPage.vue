<template>
  <div class="shop-page">
    <TopAppBar
      :name="profile.name"
      :tier="profile.tier"
      :level="profile.level"
      :avatar-url="profile.avatarUrl"
      :frame-style="profile.frameStyle"
      :frame-asset-url="profile.frameAssetUrl"
    />

    <main class="content">
      <LoadingSpinner v-if="loading" label="Memuat shop..." />

      <template v-else>
        <section class="wallet-card">
          <div class="wallet-row">
            <div class="wallet-stat">
              <span class="material-symbols-outlined wallet-icon">diamond</span>
              <span class="wallet-value">{{ diamonds }}</span>
            </div>
            <div class="wallet-divider"></div>
            <div class="wallet-stat">
              <span class="material-symbols-outlined wallet-icon">confirmation_number</span>
              <span class="wallet-value">{{ voteTickets }}</span>
            </div>
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

        <p v-if="justUnlockedAvatar" class="avatar-unlocked-banner">
          <span class="material-symbols-outlined">face</span>
          Avatar baru terkunci! <router-link to="/avatars">Pakai sekarang →</router-link>
        </p>

        <section class="shop-grid">
          <div v-for="item in filteredItems" :key="item.id" class="shop-card">
            <div class="shop-icon" :class="`icon-${item.color}`">
              <span class="material-symbols-outlined">{{ item.icon }}</span>
            </div>
            <div class="shop-body">
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
              <div class="shop-footer">
                <div class="shop-cost">
                  <span class="material-symbols-outlined cost-icon">diamond</span>
                  <span>{{ item.costDiamonds }}</span>
                </div>
                <button
                  class="buy-btn"
                  :class="{ bought: justBoughtId === item.id }"
                  :disabled="!item.inStock || diamonds < item.costDiamonds || purchasingId === item.id"
                  @click="handlePurchase(item)"
                >
                  <span v-if="!item.inStock">SOLD OUT</span>
                  <span v-else-if="purchasingId === item.id">...</span>
                  <span v-else-if="justBoughtId === item.id">BOUGHT!</span>
                  <span v-else>BUY</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        <p v-if="filteredItems.length === 0" class="empty-text">
          Belum ada item di kategori ini.
        </p>
      </template>
    </main>

    <BottomNav />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { cachedApiGet, invalidate } from '../lib/api'
import { getUser, getFrame } from '../lib/auth'
import TopAppBar from './TopAppBar.vue'
import BottomNav from './BottomNav.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const profile = ref({ 
  name: 'Producer', 
  tier: 'DIAMOND SUPPORTER', 
  level: 1, 
  avatarUrl: '',
  frameStyle: 'none',
  frameAssetUrl: ''
})

const diamonds = ref(0)
const voteTickets = ref(0)
const items = ref([])
const loading = ref(true)
const purchasingId = ref(null)
const justBoughtId = ref(null)
const justUnlockedAvatar = ref(false)

const categories = [
  { value: 'all', label: 'ALL' },
  { value: 'tickets', label: 'TICKETS' },
  { value: 'boosts', label: 'BOOSTS' },
  { value: 'avatar', label: 'AVATARS' },
  { value: 'frame', label: 'FRAMES' },
]
const activeCategory = ref('all')

const filteredItems = computed(() =>
  activeCategory.value === 'all'
    ? items.value
    : items.value.filter((i) => i.category === activeCategory.value)
)

async function handlePurchase(item) {
  if (purchasingId.value) return
  purchasingId.value = item.id
  justUnlockedAvatar.value = false
  try {
    const { data } = await api.post(`/shop/${item.id}/purchase`)
    diamonds.value = data.remainingDiamonds
    voteTickets.value = data.remainingTickets
    justBoughtId.value = item.id

    // FIX: sebelumnya item kategori avatar bisa dibeli tapi tidak pernah
    // bisa dipakai di mana pun. Sekarang backend mencatat kepemilikannya
    // (producer_inventory) dan di sini kita arahkan user ke halaman
    // /avatars untuk langsung memakainya.
    if (data.unlockedAvatar) {
      justUnlockedAvatar.value = true
      invalidate('/inventory/avatars')
    }

    // Saldo diamond/tiket berubah -> semua halaman yang menampilkannya
    // perlu ambil data baru, bukan dari cache lama.
    invalidate('/dashboard/summary')
    invalidate('/profile/me')
    invalidate('/vote/summary')

    setTimeout(() => {
      if (justBoughtId.value === item.id) justBoughtId.value = null
    }, 1500)
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal melakukan pembelian')
  } finally {
    purchasingId.value = null
  }
}

async function loadShop({ force = false } = {}) {
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
    const data = await cachedApiGet('/shop', { ttl: 60 * 1000, force })
    diamonds.value = data.diamonds
    voteTickets.value = data.voteTickets
    items.value = data.items
  } catch (err) {
    console.error('Failed to load shop', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadShop())
</script>

<style scoped>
.shop-page {
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

/* Wallet */
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
  gap: 8px;
}
.wallet-icon {
  color: #b5c4ff;
  font-size: 22px;
  font-variation-settings: 'FILL' 1;
}
.wallet-value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}
.wallet-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
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

.avatar-unlocked-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(181, 196, 255, 0.1);
  border: 1px solid rgba(181, 196, 255, 0.3);
  font-size: 12px;
  font-weight: 700;
  color: #b5c4ff;
}
.avatar-unlocked-banner a { color: #dce1fc; text-decoration: underline; }

/* Shop cards */
.shop-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.shop-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.shop-icon {
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
.shop-body { flex: 1; min-width: 0; }
.shop-body h3 {
  font-size: 15px;
  font-weight: 700;
  margin: 0;
  color: #dce1fc;
}
.shop-body p {
  font-size: 12px;
  color: #c3c5d7;
  margin: 4px 0 0;
}
.shop-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}
.shop-cost {
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
.buy-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  border: none;
  cursor: pointer;
  background: linear-gradient(90deg, #4f7dff, #3d66d6);
  color: #00297a;
  box-shadow: 0 4px 12px rgba(79, 125, 255, 0.3);
}
.buy-btn:disabled {
  background: rgba(255, 255, 255, 0.05);
  color: #c3c5d7;
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}
.buy-btn.bought {
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
