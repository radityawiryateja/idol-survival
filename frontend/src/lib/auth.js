// Local session storage helpers. Swap for a Pinia store if the app grows.
const TOKEN_KEY = 'idol_survival_session_token'
const USER_KEY = 'idol_survival_user'

export function saveSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function getSessionToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function isAuthenticated() {
  return !!getSessionToken()
}
