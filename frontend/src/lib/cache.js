// Client-side cache sederhana, murni in-memory (JS Map).
//
// Kenapa in-memory, bukan localStorage/sessionStorage?
// Ini SPA — pindah halaman via vue-router TIDAK reload module JS, jadi
// Map ini tetap hidup selama user berpindah-pindah page (persis yang
// diminta: jangan fetch ulang data yang sama tiap ganti halaman).
// Begitu user benar-benar F5 / reload tab, seluruh module JS di-reset
// oleh browser, termasuk Map ini — jadi "refetch hanya saat refresh"
// otomatis terpenuhi tanpa perlu logic tambahan.

const store = new Map() // key -> { data, expiresAt }
const inflight = new Map() // key -> Promise, biar request bersamaan tidak dobel

const DEFAULT_TTL_MS = 5 * 60 * 1000 // 5 menit

export function cacheGet(key) {
  const entry = store.get(key)
  if (!entry) return undefined
  if (entry.expiresAt && Date.now() > entry.expiresAt) {
    store.delete(key)
    return undefined
  }
  return entry.data
}

export function cacheSet(key, data, ttl = DEFAULT_TTL_MS) {
  store.set(key, { data, expiresAt: ttl ? Date.now() + ttl : null })
}

// Hapus 1 key persis, atau semua key yang diawali prefix tertentu
// (mis. invalidate('/idols') juga menghapus '/idols?season=...').
export function cacheInvalidate(prefixOrKey) {
  for (const key of store.keys()) {
    if (key === prefixOrKey || key.startsWith(prefixOrKey)) {
      store.delete(key)
    }
  }
}

export function cacheClearAll() {
  store.clear()
  inflight.clear()
}

/**
 * Ambil dari cache kalau ada & belum expired; kalau tidak, jalankan
 * fetcher() sekali, simpan hasilnya, dan dedupe request yang bersamaan
 * untuk key yang sama.
 */
export async function withCache(key, fetcher, { ttl = DEFAULT_TTL_MS, force = false } = {}) {
  if (!force) {
    const cached = cacheGet(key)
    if (cached !== undefined) return cached

    if (inflight.has(key)) return inflight.get(key)
  }

  const promise = fetcher()
    .then((data) => {
      cacheSet(key, data, ttl)
      inflight.delete(key)
      return data
    })
    .catch((err) => {
      inflight.delete(key)
      throw err
    })

  inflight.set(key, promise)
  return promise
}
