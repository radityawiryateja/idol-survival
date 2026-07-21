// Local session storage helpers. Swap for a Pinia store if the app grows.
const TOKEN_KEY = 'idol_survival_session_token'
const USER_KEY = 'idol_survival_user'
const ROLE_KEY = 'idol_survival_role'

// role sekarang jadi parameter eksplisit (bukan ditebak dari `user`)
// supaya router guard bisa baca cepat tanpa parse ulang objek user.
export function saveSession(token, user, role = 'producer') {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
  localStorage.setItem(ROLE_KEY, role)
}

export function getSessionToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function getRole() {
  return localStorage.getItem(ROLE_KEY) || 'producer'
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem(ROLE_KEY)
}

export function isAuthenticated() {
  return !!getSessionToken()
}

export function hasRole(...roles) {
  return roles.includes(getRole())
}
