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
      <!-- Telegram injects its own iframe button into this container -->
      <div ref="telegramWidget" class="telegram-widget-container"></div>

      <p v-if="loading" class="loading-text">Signing you in...</p>
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
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../lib/api'
import { saveSession } from '../lib/auth'

const router = useRouter()
const telegramWidget = ref(null)
const loading = ref(false)
const errorMessage = ref('')

const BOT_USERNAME = import.meta.env.VITE_TELEGRAM_BOT_USERNAME

// Loads the official Telegram Login Widget script and configures it to
// call window.onTelegramAuth(user) once the person authorizes.
function loadTelegramWidgetScript() {
  return new Promise((resolve, reject) => {
    if (document.getElementById('telegram-login-script')) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.id = 'telegram-login-script'
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.async = true
    script.setAttribute('data-telegram-login', BOT_USERNAME)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-radius', '12')
    script.setAttribute('data-onauth', 'onTelegramAuth(user)')
    script.setAttribute('data-request-access', 'write')
    script.onload = resolve
    script.onerror = reject
    telegramWidget.value.appendChild(script)
  })
}

// Callback invoked by Telegram's widget with the signed user object.
// We forward it as-is to the backend, which re-verifies the HMAC hash —
// the frontend never trusts this data on its own.
async function handleTelegramAuth(user) {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.post('/auth/telegram-callback', user)
    saveSession(data.session_token, data.user)
    router.push({ name: 'dashboard' })
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail || 'Gagal login dengan Telegram. Coba lagi.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  window.onTelegramAuth = handleTelegramAuth
  loadTelegramWidgetScript().catch(() => {
    errorMessage.value = 'Gagal memuat widget Telegram Login.'
  })
})

onBeforeUnmount(() => {
  delete window.onTelegramAuth
})
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
