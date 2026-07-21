import axios from 'axios'
import { clearSession, getSessionToken } from './auth'
import { withCache, cacheInvalidate, cacheClearAll } from './cache'

const api = axios.create({
  baseURL: 'https://rolesurvival.my.id/api',
})

// Attach the session token (issued by the backend after Telegram login)
// to every outgoing request.
api.interceptors.request.use((config) => {
  const token = getSessionToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// If the backend says the session is no longer valid, drop it locally too.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearSession()
      cacheClearAll()
    }
    return Promise.reject(error)
  }
)

/**
 * GET yang di-cache di klien. Dipakai menggantikan `api.get(url)` polos
 * di halaman-halaman yang datanya tidak perlu selalu real-time (dashboard,
 * daftar idol, leaderboard, shop, dst). Data hanya diambil ulang dari
 * backend kalau: cache-nya sudah expired (TTL), user melakukan aksi yang
 * mengubah data itu sendiri (lihat `invalidate`), atau halaman di-reload.
 *
 * @param {string} url
 * @param {{params?: object, ttl?: number, force?: boolean}} options
 */
export async function cachedApiGet(url, { params, ttl, force = false } = {}) {
  const key = params ? `${url}?${JSON.stringify(params)}` : url
  return withCache(
    key,
    async () => {
      const { data } = await api.get(url, { params })
      return data
    },
    { ttl, force }
  )
}

/** Hapus cache untuk 1 endpoint (atau semua endpoint berawalan `prefix`)
 * setelah mutasi (vote, purchase, claim, dsb) supaya halaman lain yang
 * menampilkan data terkait langsung sinkron tanpa menunggu TTL habis. */
export function invalidate(prefix) {
  cacheInvalidate(prefix)
}

export default api
