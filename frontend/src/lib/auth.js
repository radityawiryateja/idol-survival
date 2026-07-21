// Local session storage helpers. Swap for a Pinia store if the app grows.
const TOKEN_KEY = 'idol_survival_session_token'
const USER_KEY = 'idol_survival_user'
const ROLE_KEY = 'idol_survival_role'
const FRAME_KEY = 'idol_survival_frame'

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

// Cache ringan buat equipped frame, diisi tiap kali /profile/me atau
// /dashboard/summary balikin equippedFrame, dibaca semua halaman lain
// yang pakai TopAppBar supaya frame kelihatan konsisten di semua page
// tanpa harus fetch API tambahan di tiap halaman.
export function saveFrame(frame) {
  if (frame) {
    localStorage.setItem(FRAME_KEY, JSON.stringify(frame))
  } else {
    localStorage.removeItem(FRAME_KEY)
  }
}

export function getFrame() {
  const raw = localStorage.getItem(FRAME_KEY)
  return raw ? JSON.parse(raw) : null
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem(ROLE_KEY)
  localStorage.removeItem(FRAME_KEY)
}

export function isAuthenticated() {
  return !!getSessionToken()
}

export function hasRole(...roles) {
  return roles.includes(getRole())
}
