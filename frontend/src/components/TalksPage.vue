<template>
  <div class="talks-page">
    <!-- ROOM LIST -->
    <template v-if="!activeRoom">
      <TopAppBar
        :name="profile.name"
        :tier="profile.tier"
        :level="profile.level"
        :avatar-url="profile.avatarUrl"
      />
      <main class="content">
        <section class="page-title">
          <h1>Talks</h1>
          <p>Pesan pribadi dari idol favoritmu.</p>
        </section>

        <section class="room-list">
          <button
            v-for="room in rooms"
            :key="room.idolId"
            class="room-row"
            @click="openRoom(room)"
          >
            <div class="room-avatar">
              <img :src="room.photo" :alt="room.name" />
            </div>
            <div class="room-info">
              <h3>{{ room.name }}</h3>
              <p>{{ room.lastMessagePreview }}</p>
            </div>
            <span v-if="room.lastMessageAt" class="room-time">{{ formatTime(room.lastMessageAt) }}</span>
          </button>
        </section>

        <p v-if="!loadingRooms && rooms.length === 0" class="empty-text">Belum ada idol untuk diajak ngobrol.</p>
      </main>
      <BottomNav />
    </template>

    <!-- CHAT ROOM -->
    <template v-else>
      <header class="chat-top-bar">
        <button class="back-btn" @click="closeRoom" aria-label="Back">
          <span class="material-symbols-outlined">arrow_back_ios_new</span>
        </button>
        <div class="chat-header-info">
          <img :src="activeRoom.photo" :alt="activeRoom.name" class="chat-avatar" />
          <h2>{{ activeRoom.name }}</h2>
        </div>
        <div class="chat-header-spacer"></div>
      </header>

      <main class="chat-messages" ref="messagesEl">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="bubble-row"
          :class="{ mine: msg.sender === 'user' }"
        >
          <img v-if="msg.sender === 'idol'" :src="activeRoom.photo" class="bubble-avatar" />
          <div class="bubble" :class="{ mine: msg.sender === 'user', broadcast: msg.scope === 'broadcast' }">
            <img v-if="msg.mediaType === 'photo'" :src="msg.mediaUrl" class="bubble-media" />
            <p v-if="msg.content">{{ msg.content }}</p>
            <span class="bubble-time">{{ formatTime(msg.createdAt) }}</span>
          </div>
        </div>
        <p v-if="messages.length === 0" class="empty-text">Belum ada pesan. Mulai obrolan!</p>
      </main>

      <form class="chat-input-bar" @submit.prevent="handleSend">
        <input
          v-model="draft"
          type="text"
          placeholder="Ketik pesan..."
          class="chat-input"
          :disabled="sending"
        />
        <button type="submit" class="send-btn" :disabled="!draft.trim() || sending" aria-label="Send">
          <span class="material-symbols-outlined">send</span>
        </button>
      </form>
    </template>
  </div>
</template>

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import api from '../lib/api'
import { getUser } from '../lib/auth'
import { supabase } from '../lib/supabase'
import TopAppBar from './TopAppBar.vue'
import BottomNav from './BottomNav.vue'

const profile = ref({ name: 'Producer', tier: 'DIAMOND SUPPORTER', level: 1, avatarUrl: '' })

const rooms = ref([])
const loadingRooms = ref(true)
const activeRoom = ref(null)
const messages = ref([])
const draft = ref('')
const sending = ref(false)
const messagesEl = ref(null)

let pollTimer = null
let realtimeChannel = null

function formatTime(isoString) {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

async function loadRooms() {
  loadingRooms.value = true
  try {
    const { data } = await api.get('/talks/rooms')
    rooms.value = data.rooms
  } catch (err) {
    console.error('Failed to load talk rooms', err)
  } finally {
    loadingRooms.value = false
  }
}

async function loadMessages(idolId) {
  try {
    const { data } = await api.get(`/talks/${idolId}/messages`)
    messages.value = data.messages
    scrollToBottom()
  } catch (err) {
    console.error('Failed to load messages', err)
  }
}

// Broadcast idol bersifat publik -> aman dipantau langsung lewat Supabase
// Realtime pakai anon key. Private message TIDAK dipantau lewat sini,
// tapi lewat polling ke FastAPI (lihat startPolling), karena app ini
// pakai session JWT sendiri (bukan Supabase Auth) jadi RLS per-user
// nggak bisa diandalkan lewat anon key untuk data privat.
function subscribeToBroadcasts(idolId) {
  realtimeChannel = supabase
    .channel(`idol-broadcasts-${idolId}`)
    .on(
      'postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'idol_broadcasts', filter: `idol_id=eq.${idolId}` },
      (payload) => {
        messages.value.push({
          id: payload.new.id,
          sender: 'idol',
          scope: 'broadcast',
          content: payload.new.content,
          mediaUrl: payload.new.media_url,
          mediaType: payload.new.media_type,
          createdAt: payload.new.created_at,
        })
        scrollToBottom()
      }
    )
    .subscribe()
}

function startPolling(idolId) {
  pollTimer = setInterval(() => loadMessages(idolId), 4000)
}

function stopLiveUpdates() {
  if (pollTimer) clearInterval(pollTimer)
  if (realtimeChannel) supabase.removeChannel(realtimeChannel)
  pollTimer = null
  realtimeChannel = null
}

async function openRoom(room) {
  activeRoom.value = room
  await loadMessages(room.idolId)
  subscribeToBroadcasts(room.idolId)
  startPolling(room.idolId)
}

function closeRoom() {
  stopLiveUpdates()
  activeRoom.value = null
  messages.value = []
  loadRooms() // refresh preview terakhir di list
}

async function handleSend() {
  const content = draft.value.trim()
  if (!content || sending.value) return

  sending.value = true
  // Optimistic append biar berasa instan
  const optimisticId = `temp-${Date.now()}`
  messages.value.push({
    id: optimisticId,
    sender: 'user',
    scope: 'private',
    content,
    mediaType: 'text',
    createdAt: new Date().toISOString(),
  })
  draft.value = ''
  scrollToBottom()

  try {
    await api.post(`/talks/${activeRoom.value.idolId}/messages`, { content })
  } catch (err) {
    console.error('Failed to send message', err)
    messages.value = messages.value.filter((m) => m.id !== optimisticId)
    alert('Gagal mengirim pesan')
  } finally {
    sending.value = false
  }
}

onMounted(() => {
  const cachedUser = getUser()
  if (cachedUser) {
    profile.value.name = cachedUser.first_name || 'Producer'
    profile.value.avatarUrl = cachedUser.photo_url || ''
  }
  loadRooms()
})

onUnmounted(stopLiveUpdates)
</script>

<style scoped>
.talks-page {
  min-height: 100dvh;
  background: #0d1226;
  color: #dce1fc;
  display: flex;
  flex-direction: column;
}

/* Room list */
.content {
  max-width: 480px;
  margin: 0 auto;
  width: 100%;
  padding: 96px 20px 128px;
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
.room-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.room-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  text-align: left;
}
.room-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid rgba(181, 196, 255, 0.3);
  flex-shrink: 0;
}
.room-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #191f32;
}
.room-info { flex: 1; min-width: 0; }
.room-info h3 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: #dce1fc;
}
.room-info p {
  font-size: 13px;
  color: #c3c5d7;
  margin: 2px 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.room-time {
  font-size: 11px;
  color: rgba(195, 197, 215, 0.5);
  flex-shrink: 0;
}
.empty-text {
  text-align: center;
  font-size: 13px;
  color: rgba(195, 197, 215, 0.6);
  padding: 24px 0;
}

/* Chat room */
.chat-top-bar {
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
.chat-header-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  justify-content: center;
}
.chat-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(181, 196, 255, 0.3);
}
.chat-header-info h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}
.chat-header-spacer { width: 40px; }

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 80px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 480px;
  margin: 0 auto;
  width: 100%;
}
.bubble-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
.bubble-row.mine {
  flex-direction: row-reverse;
}
.bubble-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}
.bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 16px;
  background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom-left-radius: 4px;
}
.bubble.mine {
  background: linear-gradient(90deg, #4f7dff, #3d66d6);
  border: none;
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 4px;
  color: #00133d;
}
.bubble.broadcast {
  border-color: rgba(181, 196, 255, 0.4);
  box-shadow: 0 0 12px rgba(79, 125, 255, 0.15);
}
.bubble p {
  margin: 0;
  font-size: 14px;
  line-height: 1.4;
  color: inherit;
}
.bubble:not(.mine) p { color: #dce1fc; }
.bubble-media {
  width: 100%;
  border-radius: 10px;
  margin-bottom: 6px;
  display: block;
}
.bubble-time {
  display: block;
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.6;
}

.chat-input-bar {
  position: sticky;
  bottom: 0;
  display: flex;
  gap: 8px;
  padding: 12px 16px calc(12px + env(safe-area-inset-bottom));
  background: rgba(13, 18, 38, 0.9);
  backdrop-filter: blur(24px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 480px;
  margin: 0 auto;
  width: 100%;
}
.chat-input {
  flex: 1;
  background: #191f32;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 10px 16px;
  color: #dce1fc;
  font-size: 14px;
}
.chat-input:focus {
  outline: none;
  border-color: #4f7dff;
}
.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #b5c4ff;
  color: #00297a;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
