<template>
  <div class="login-page">
    <header class="header">
      <h1 class="brand-title">IDOL SURVIVAL</h1>
      <div class="welcome-text">
        <h2>Welcome Back, Producer</h2>
        <p>Sign in to manage your talent roster</p>
      </div>
    </header>

    <div class="orb-wrap">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="orb-core">
        <span class="material-symbols-outlined">fingerprint</span>
      </div>
    </div>

    <main class="content">
      <!-- Sembunyikan tombol kalau sedang proses Auto-Login di Web App -->
      <button 
        v-if="!isWebApp" 
        class="telegram-login-btn" 
        @click="startTelegramLogin"
        :disabled="loading"
      >
        <span class="material-symbols-outlined">send</span>
        Login with Telegram
      </button>

      <p v-if="loading" class="loading-text">{{ loadingText }}</p>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    </main>

    <footer class="footer-links">
      <a href="#">TERMS OF SERVICE</a>
      <span>•</span>
      <a href="#">PRIVACY POLICY</a>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../lib/api'
import { saveSession } from '../lib/auth'
import { generateCodeChallenge, generateRandomString } from '../lib/pkce'

const router = useRouter()
const loading = ref(false)
const isWebApp = ref(false)
const errorMessage = ref('')
const loadingText = ref('Signing you in...')

const CLIENT_ID = import.meta.env.VITE_TELEGRAM_OIDC_CLIENT_ID
const REDIRECT_URI = import.meta.env.VITE_TELEGRAM_OIDC_REDIRECT_URI

onMounted(async () => {
  const tg = window.Telegram?.WebApp
  
  // Jika terdapat initData, berarti aplikasi dibuka langsung via Telegram Mini App
  if (tg && tg.initData) {
    isWebApp.value = true
    loading.value = true
    loadingText.value = 'Auto-authenticating with Telegram...'
    
    try {
      // Hit endpoint baru menggunakan initData (tanpa perlu lewat OIDC redirection)
      const { data } = await api.post('/auth/webapp-login', {
        init_data: tg.initData
      })
      
      saveSession(data.session_token, data.user)
      router.push({ name: 'dashboard' })
    } catch (err) {
      console.error(err)
      isWebApp.value = false // Tampilkan lagi tombol manual jika auto-login gagal
      errorMessage.value = err.response?.data?.detail || 'Auto-login gagal.'
    } finally {
      loading.value = false
    }
  }
})

// Fungsi lama untuk fallback login dari eksternal browser
async function startTelegramLogin() {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const state = generateRandomString(32)
    const codeVerifier = generateRandomString(64)
    const codeChallenge = await generateCodeChallenge(codeVerifier)

    sessionStorage.setItem('tg_oidc_state', state)
    sessionStorage.setItem('tg_oidc_verifier', codeVerifier)

    const authUrl = new URL('https://oauth.telegram.org/auth')
    authUrl.searchParams.set('client_id', CLIENT_ID)
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI)
    authUrl.searchParams.set('response_type', 'code')
    authUrl.searchParams.set('scope', 'openid profile phone')
    authUrl.searchParams.set('state', state)
    authUrl.searchParams.set('code_challenge', codeChallenge)
    authUrl.searchParams.set('code_challenge_method', 'S256')

    window.location.href = authUrl.toString()
  } catch (err) {
    loading.value = false
    errorMessage.value = 'Gagal memulai login eksternal.'
  }
}

defineExpose({ startTelegramLogin })
</script>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 20px;
  background-color: #0d1226;
  color: #dce1fc;
}
.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
  text-align: center;
}
.brand-title {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 12px;
}
.welcome-text h2 {
  color: #b5c4ff;
  font-weight: 600;
  margin: 0;
}
.welcome-text p {
  opacity: 0.7;
  font-size: 14px;
  margin: 4px 0 0;
}
.orb-wrap {
  position: relative;
  width: 280px;
  height: 280px;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}
.orb {
  position: absolute;
  border-radius: 50%;
  animation: pulse-glow 8s infinite alternate ease-in-out;
}
.orb-1 {
  width: 192px;
  height: 192px;
  background: rgba(181, 196, 255, 0.2);
  filter: blur(40px);
}
.orb-2 {
  width: 128px;
  height: 128px;
  border: 2px solid rgba(181, 196, 255, 0.4);
  animation-delay: -2s;
}
.orb-3 {
  width: 160px;
  height: 160px;
  border: 1px solid rgba(197, 192, 255, 0.3);
  animation-delay: -4s;
}
.orb-core {
  position: relative;
  z-index: 10;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: rgba(20, 28, 52, 0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b5c4ff;
}
@keyframes pulse-glow {
  0% { transform: scale(1) rotate(0deg); opacity: 0.8; }
  50% { transform: scale(1.1) rotate(180deg); opacity: 1; }
  100% { transform: scale(1) rotate(360deg); opacity: 0.8; }
}
  .telegram-login-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  border-radius: 12px;
  background: #4f7dff;
  color: #fff;
  font-weight: 700;
  border: none;
  cursor: pointer;
  font-size: 15px;
}
.telegram-login-btn:hover {
  opacity: 0.9;
}
.content {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.telegram-widget-container {
  display: flex;
  justify-content: center;
  min-height: 40px;
}
.error-text {
  color: #ffb4ab;
  font-size: 14px;
  margin: 0;
}
.loading-text {
  color: #b5c4ff;
  font-size: 14px;
  margin: 0;
}
.footer-links {
  margin-top: auto;
  padding-top: 32px;
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: rgba(220, 225, 252, 0.4);
}
.footer-links a {
  text-decoration: none;
  color: inherit;
}
</style>
