<template>
  <div class="avatar-page">
    <header class="top-bar">
      <button class="back-btn" @click="$router.back()" aria-label="Back">
        <span class="material-symbols-outlined">arrow_back_ios_new</span>
      </button>
      <h2>My Collection</h2>
      <div class="spacer"></div>
    </header>

    <main class="content">
      <section class="tabs-row">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'avatar' }"
          @click="activeTab = 'avatar'"
        >
          Avatars
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'frame' }"
          @click="activeTab = 'frame'"
        >
          Frames
        </button>
      </section>

      <!-- ============ AVATAR TAB ============ -->
      <template v-if="activeTab === 'avatar'">
        <LoadingSpinner v-if="loadingAvatars" label="Memuat koleksi avatar..." />

        <template v-else>
          <p class="hint-text">
            Avatar yang kamu beli di Shop muncul di sini. Tap salah satu untuk memakainya
            sebagai foto profil di dalam app.
          </p>

          <section class="grid">
            <button class="slot" :class="{ active: usingDefaultAvatar }" @click="handleResetAvatar">
              <AvatarFrame :avatar-url="defaultAvatarUrl" :frame-style="previewFrameStyle" :frame-asset-url="previewFrameAssetUrl" :size="64" />
              <span class="slot-label">Default</span>
              <span v-if="usingDefaultAvatar" class="check-badge material-symbols-outlined">check_circle</span>
            </button>

            <button
              v-for="avatar in avatars"
              :key="avatar.id"
              class="slot"
              :class="{ active: avatar.equipped }"
              :disabled="equippingAvatarId === avatar.id"
              @click="handleEquipAvatar(avatar)"
            >
              <AvatarFrame :avatar-url="avatar.assetUrl" :frame-style="previewFrameStyle" :frame-asset-url="previewFrameAssetUrl" :size="64" />
              <span class="slot-label">{{ avatar.title }}</span>
              <span v-if="avatar.equipped" class="check-badge material-symbols-outlined">check_circle</span>
            </button>
          </section>

          <p v-if="avatars.length === 0" class="empty-text">
            Kamu belum punya avatar limited. Beli di
            <router-link to="/shop">Shop</router-link> kategori "Cosmetics".
          </p>
        </template>
      </template>

      <!-- ============ FRAME TAB ============ -->
      <template v-else>
        <LoadingSpinner v-if="loadingFrames" label="Memuat koleksi frame..." />

        <template v-else>
          <p class="hint-text">
            Frame adalah border animasi di sekeliling avatar kamu. Beli di Shop kategori "Frame".
          </p>

          <section class="grid">
            <button class="slot" :class="{ active: !equippedFrame }" @click="handleResetFrame">
              <AvatarFrame :avatar-url="previewAvatarUrl" frame-style="none" :size="64" />
              <span class="slot-label">No Frame</span>
              <span v-if="!equippedFrame" class="check-badge material-symbols-outlined">check_circle</span>
            </button>

            <button
              v-for="frame in frames"
              :key="frame.id"
              class="slot"
              :class="{ active: frame.equipped }"
              :disabled="equippingFrameId === frame.id"
              @click="handleEquipFrame(frame)"
            >
              <AvatarFrame :avatar-url="previewAvatarUrl" :frame-style="frame.frameStyle" :frame-asset-url="frame.frameAssetUrl" :size="64" />
              <span class="slot-label">{{ frame.title }}</span>
              <span class="rarity-tag" :class="`rarity-${frame.rarity}`">{{ frame.rarity }}</span>
              <span v-if="frame.equipped" class="check-badge material-symbols-outlined">check_circle</span>
            </button>
          </section>

          <p v-if="frames.length === 0" class="empty-text">
            Kamu belum punya frame. Beli di <router-link to="/shop">Shop</router-link> kategori "Frame".
          </p>
        </template>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { cachedApiGet, invalidate } from '../lib/api'
import { getUser, saveFrame } from '../lib/auth'
import AvatarFrame from './AvatarFrame.vue'
import LoadingSpinner from './LoadingSpinner.vue'

const activeTab = ref('avatar')

// ---------- Avatar tab ----------
const loadingAvatars = ref(true)
const defaultAvatarUrl = ref('')
const usingDefaultAvatar = ref(true)
const avatars = ref([])
const equippingAvatarId = ref(null)

async function loadAvatars() {
  loadingAvatars.value = true
  try {
    const data = await cachedApiGet('/inventory/avatars', { ttl: 60 * 1000 })
    defaultAvatarUrl.value = data.defaultAvatarUrl
    usingDefaultAvatar.value = data.usingDefault
    avatars.value = data.avatars
  } catch (err) {
    console.error('Failed to load avatar inventory', err)
  } finally {
    loadingAvatars.value = false
  }
}

async function handleEquipAvatar(avatar) {
  if (equippingAvatarId.value) return
  equippingAvatarId.value = avatar.id
  try {
    await api.post(`/inventory/avatars/${avatar.id}/equip`)
    invalidateProfileCaches()
    await loadAvatars()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal memakai avatar ini')
  } finally {
    equippingAvatarId.value = null
  }
}

async function handleResetAvatar() {
  if (usingDefaultAvatar.value || equippingAvatarId.value) return
  equippingAvatarId.value = 'default'
  try {
    await api.post('/inventory/avatars/reset')
    invalidateProfileCaches()
    await loadAvatars()
  } catch (err) {
    console.error('Failed to reset avatar', err)
  } finally {
    equippingAvatarId.value = null
  }
}

// ---------- Frame tab ----------
const loadingFrames = ref(true)
const equippedFrame = ref(null) // {style, assetUrl, rarity} | null
const frames = ref([])
const equippingFrameId = ref(null)

async function loadFrames() {
  loadingFrames.value = true
  try {
    const data = await cachedApiGet('/inventory/frames', { ttl: 60 * 1000 })
    equippedFrame.value = data.equipped
    frames.value = data.frames
  } catch (err) {
    console.error('Failed to load frame inventory', err)
  } finally {
    loadingFrames.value = false
  }
}

async function handleEquipFrame(frame) {
  if (equippingFrameId.value) return
  equippingFrameId.value = frame.id
  try {
    await api.post(`/inventory/frames/${frame.id}/equip`)
    invalidate('/inventory/frames')
    saveFrame({ style: frame.frameStyle, assetUrl: frame.frameAssetUrl, rarity: frame.rarity })
    invalidateProfileCaches()
    await loadFrames()
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal memakai frame ini')
  } finally {
    equippingFrameId.value = null
  }
}

async function handleResetFrame() {
  if (!equippedFrame.value || equippingFrameId.value) return
  equippingFrameId.value = 'none'
  try {
    await api.post('/inventory/frames/reset')
    invalidate('/inventory/frames')
    saveFrame(null)
    invalidateProfileCaches()
    await loadFrames()
  } catch (err) {
    console.error('Failed to reset frame', err)
  } finally {
    equippingFrameId.value = null
  }
}

// ---------- Shared ----------
// Preview avatar dipakai di tab Frame (avatar apapun yang lagi kepake si producer)
const previewAvatarUrl = computed(() => {
  const cachedUser = getUser()
  return cachedUser?.photo_url || ''
})
// Preview frame dipakai di tab Avatar (biar avatar-slot kelihatan sama kayak equipped frame)
const previewFrameStyle = computed(() => equippedFrame.value?.style || 'none')
const previewFrameAssetUrl = computed(() => equippedFrame.value?.assetUrl || '')

function invalidateProfileCaches() {
  invalidate('/inventory/avatars')
  invalidate('/inventory/frames')
  invalidate('/profile/me')
  invalidate('/dashboard/summary')
}

onMounted(() => {
  loadAvatars()
  loadFrames()
})
</script>

<style scoped>
.avatar-page { min-height: 100dvh; background: #0d1226; color: #dce1fc; }
.top-bar {
  position: fixed; top: 0; left: 0; width: 100%; z-index: 50;
  background: rgba(13, 18, 38, 0.8); backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; justify-content: space-between;
  height: 64px; padding: 0 12px;
}
.back-btn {
  width: 40px; height: 40px; border-radius: 50%; background: none; border: none;
  color: #b5c4ff; display: flex; align-items: center; justify-content: center; cursor: pointer;
}
.back-btn:hover { background: rgba(255, 255, 255, 0.05); }
.top-bar h2 { font-size: 16px; font-weight: 700; margin: 0; }
.spacer { width: 40px; }
.content {
  max-width: 480px; margin: 0 auto; padding: 96px 20px 48px;
  display: flex; flex-direction: column; gap: 20px;
}
.tabs-row { display: flex; gap: 8px; }
.tab-btn {
  flex: 1; padding: 10px; border-radius: 12px; background: #23293d;
  border: 1px solid rgba(255,255,255,0.05); color: #c3c5d7;
  font-size: 12px; font-weight: 700; letter-spacing: 0.05em; cursor: pointer;
}
.tab-btn.active { background: #b5c4ff; color: #00297a; border-color: transparent; }
.hint-text { font-size: 12px; color: rgba(195, 197, 215, 0.7); line-height: 1.5; margin: 0; }
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.slot {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 2px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
}
.slot.active { border-color: #b5c4ff; box-shadow: 0 0 12px rgba(79, 125, 255, 0.3); }
.slot:disabled { opacity: 0.5; cursor: wait; }
.slot-label {
  font-size: 10px; font-weight: 700; text-align: center; color: #c3c5d7;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 100%;
}
.rarity-tag {
  font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
  padding: 1px 6px; border-radius: 999px;
}
.rarity-common { background: rgba(195,197,215,0.15); color: #c3c5d7; }
.rarity-rare { background: rgba(79,125,255,0.15); color: #4f7dff; }
.rarity-epic { background: rgba(168,85,247,0.15); color: #a855f7; }
.rarity-legendary { background: rgba(255,215,0,0.15); color: #ffd700; }
.check-badge {
  position: absolute; top: 4px; right: 4px; font-size: 16px; color: #34d399;
  font-variation-settings: 'FILL' 1;
}
.empty-text { text-align: center; font-size: 13px; color: rgba(195, 197, 215, 0.6); }
.empty-text a { color: #b5c4ff; }
</style>
