<template>
  <div class="callback-page">
    <p v-if="status === 'loading'">Menyelesaikan login...</p>
    <p v-else-if="status === 'error'" class="error-text">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../lib/api'
import { saveSession } from '../lib/auth'

const route = useRoute()
const router = useRouter()
const status = ref('loading')
const errorMessage = ref('')

async function handleCallback() {
  const code = route.query.code
  const returnedState = route.query.state
  const oauthError = route.query.error

  if (oauthError) {
    status.value = 'error'
    errorMessage.value = 'Login dibatalkan atau ditolak.'
    return
  }

  const expectedState = sessionStorage.getItem('tg_oidc_state')
  const codeVerifier = sessionStorage.getItem('tg_oidc_verifier')

  if (!code || !returnedState || returnedState !== expectedState || !codeVerifier) {
    status.value = 'error'
    errorMessage.value = 'Sesi login tidak valid. Coba login ulang.'
    return
  }

  try {
    const { data } = await api.post('/api/telegram-callback', {
      code,
      code_verifier: codeVerifier,
    })
    saveSession(data.session_token, data.user)
    router.push({ name: 'dashboard' })
  } catch (err) {
    status.value = 'error'
    errorMessage.value = err.response?.data?.detail || 'Gagal memverifikasi login Telegram.'
  } finally {
    sessionStorage.removeItem('tg_oidc_state')
    sessionStorage.removeItem('tg_oidc_verifier')
  }
}

onMounted(handleCallback)
</script>

<style scoped>
.callback-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0d1226;
  color: #dce1fc;
}
.error-text { color: #ffb4ab; }
</style>
