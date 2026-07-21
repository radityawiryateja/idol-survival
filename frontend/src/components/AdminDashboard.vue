<template>
  <div class="admin-page">
    <header class="top-bar">
      <h2>Admin Panel</h2>
    </header>

    <main class="content">
      <section class="tabs-row">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="tab-btn"
          :class="{ active: activeTab === tab.value }"
          @click="activeTab = tab.value"
        >
          {{ tab.label }}
        </button>
      </section>

      <!-- ============ OVERVIEW ============ -->
      <section v-if="activeTab === 'overview'" class="panel">
        <LoadingSpinner v-if="loadingOverview" label="Memuat ringkasan..." />
        <div v-else class="stat-grid">
          <div class="stat-card">
            <span class="stat-label">TOTAL PRODUCERS</span>
            <span class="stat-value">{{ overview.totalProducers }}</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">TOTAL IDOLS</span>
            <span class="stat-value">{{ overview.totalIdols }}</span>
          </div>
        </div>
      </section>

      <!-- ============ PRODUCERS / ROLES ============ -->
      <section v-if="activeTab === 'producers'" class="panel">
        <input
          v-model="producerQuery"
          type="text"
          placeholder="Cari nama, username, atau telegram ID..."
          class="search-input"
          @input="debouncedSearchProducers"
        />

        <LoadingSpinner v-if="loadingProducers" label="Mencari..." />

        <div v-else class="list">
          <div v-for="p in producers" :key="p.id" class="row-card">
            <img :src="p.photo_url" class="row-avatar" :alt="p.first_name" />
            <div class="row-info">
              <h4>{{ p.first_name }} {{ p.last_name || '' }}</h4>
              <p>@{{ p.username || '—' }} · ID: {{ p.telegram_id }}</p>
            </div>
            <select
              class="role-select"
              :value="p.role"
              @change="handleRoleChange(p, $event.target.value)"
            >
              <option value="producer">Producer</option>
              <option value="idol">Idol</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <p v-if="producers.length === 0" class="empty-text">
            {{ producerQuery ? 'Tidak ada hasil.' : 'Ketik untuk mencari producer.' }}
          </p>
        </div>
      </section>

      <!-- ============ SHOP ITEMS ============ -->
      <section v-if="activeTab === 'shop'" class="panel">
        <button class="add-btn" @click="openNewItemForm">
          <span class="material-symbols-outlined">add</span> Tambah Item Baru
        </button>

        <div v-if="showItemForm" class="item-form">
          <h4>{{ editingItemId ? 'Edit Item' : 'Item Baru' }}</h4>

          <label class="field">
            <span>Judul</span>
            <input v-model="itemForm.title" type="text" />
          </label>
          <label class="field">
            <span>Deskripsi</span>
            <input v-model="itemForm.description" type="text" />
          </label>
          <label class="field">
            <span>Kategori</span>
            <select v-model="itemForm.category">
              <option value="tickets">Tickets</option>
              <option value="boosts">Boosts</option>
              <option value="cosmetics">Cosmetics</option>
              <option value="avatar">Avatar</option>
            </select>
          </label>
          <label class="field" v-if="itemForm.category === 'avatar'">
            <span>URL Gambar Avatar (wajib)</span>
            <input v-model="itemForm.asset_url" type="text" placeholder="https://..." />
          </label>
          <label class="field">
            <span>Icon (Material Symbols)</span>
            <input v-model="itemForm.icon" type="text" placeholder="mis. diamond, face, bolt" />
          </label>
          <label class="field">
            <span>Warna Aksen</span>
            <select v-model="itemForm.color">
              <option value="primary">Primary</option>
              <option value="secondary">Secondary</option>
              <option value="tertiary">Tertiary</option>
            </select>
          </label>
          <div class="field-row">
            <label class="field">
              <span>Harga (Diamond)</span>
              <input v-model.number="itemForm.cost_diamonds" type="number" min="0" />
            </label>
            <label class="field">
              <span>Stok (kosongkan = unlimited)</span>
              <input v-model.number="itemForm.stock" type="number" min="0" />
            </label>
          </div>
          <label class="field checkbox-field">
            <input v-model="itemForm.active" type="checkbox" />
            <span>Aktif / tampil di Shop</span>
          </label>

          <div class="form-actions">
            <button class="cancel-btn" @click="closeItemForm">Batal</button>
            <button class="save-btn" :disabled="savingItem" @click="handleSaveItem">
              {{ savingItem ? 'Menyimpan...' : 'Simpan' }}
            </button>
          </div>
        </div>

        <LoadingSpinner v-if="loadingItems" label="Memuat item shop..." />
        <div v-else class="list">
          <div v-for="item in shopItems" :key="item.id" class="row-card" :class="{ inactive: !item.active }">
            <div class="item-icon" :class="`icon-${item.color}`">
              <span class="material-symbols-outlined">{{ item.icon }}</span>
            </div>
            <div class="row-info">
              <h4>{{ item.title }} <span class="cat-tag">{{ item.category }}</span></h4>
              <p>{{ item.cost_diamonds }} diamond · stok {{ item.stock ?? '∞' }} · {{ item.active ? 'Aktif' : 'Nonaktif' }}</p>
            </div>
            <button class="edit-btn" @click="openEditItemForm(item)">
              <span class="material-symbols-outlined">edit</span>
            </button>
          </div>
        </div>
      </section>

      <!-- ============ IDOL LINKING ============ -->
      <section v-if="activeTab === 'idols'" class="panel">
        <p class="hint-text">
          Tautkan akun Telegram pribadi seorang idol ke profil idol-nya di roster,
          supaya idol tersebut bisa login dan mengakses Idol Panel-nya sendiri.
        </p>

        <LoadingSpinner v-if="loadingIdols" label="Memuat daftar idol..." />
        <div v-else class="list">
          <div v-for="idol in idols" :key="idol.id" class="row-card">
            <img :src="idol.photo_url" class="row-avatar" :alt="idol.name" />
            <div class="row-info">
              <h4>{{ idol.name }}</h4>
              <p>{{ idol.agency }}</p>
              <p class="link-status">
                {{ idol.linked_producer_id ? '✅ Sudah ditautkan' : '⚠️ Belum ditautkan' }}
              </p>
            </div>
            <div class="link-actions">
              <button
                v-if="idol.linked_producer_id"
                class="unlink-btn"
                @click="handleUnlinkIdol(idol)"
              >
                Putuskan
              </button>
              <button v-else class="link-btn" @click="openLinkModal(idol)">
                Tautkan
              </button>
            </div>
          </div>
        </div>

        <!-- Modal kecil untuk cari & pilih producer yang ditautkan -->
        <div v-if="linkingIdol" class="modal-backdrop" @click.self="linkingIdol = null">
          <div class="modal-card">
            <h4>Tautkan "{{ linkingIdol.name }}" ke akun...</h4>
            <input
              v-model="linkQuery"
              type="text"
              placeholder="Cari producer..."
              class="search-input"
              @input="debouncedSearchLinkCandidates"
            />
            <div class="list">
              <button
                v-for="p in linkCandidates"
                :key="p.id"
                class="row-card candidate-row"
                @click="handleLinkIdol(p)"
              >
                <img :src="p.photo_url" class="row-avatar" />
                <div class="row-info">
                  <h4>{{ p.first_name }} {{ p.last_name || '' }}</h4>
                  <p>@{{ p.username || '—' }}</p>
                </div>
              </button>
            </div>
            <button class="cancel-btn full-width" @click="linkingIdol = null">Tutup</button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api, { cachedApiGet, invalidate } from '../lib/api'
import LoadingSpinner from './LoadingSpinner.vue'

const tabs = [
  { value: 'overview', label: 'Overview' },
  { value: 'producers', label: 'Producers' },
  { value: 'shop', label: 'Shop Items' },
  { value: 'idols', label: 'Idol Linking' },
]
const activeTab = ref('overview')

// ---------- Overview ----------
const loadingOverview = ref(true)
const overview = ref({ totalProducers: 0, totalIdols: 0 })

async function loadOverview() {
  loadingOverview.value = true
  try {
    overview.value = await cachedApiGet('/admin/overview', { ttl: 30 * 1000 })
  } finally {
    loadingOverview.value = false
  }
}

// ---------- Producers / roles ----------
const producerQuery = ref('')
const producers = ref([])
const loadingProducers = ref(false)
let producerSearchTimer = null

async function searchProducers() {
  loadingProducers.value = true
  try {
    // Tidak di-cache: hasil pencarian berubah-ubah dan admin butuh data
    // terkini tiap kali cari.
    const { data } = await api.get('/admin/producers', { params: { q: producerQuery.value } })
    producers.value = data.producers
  } catch (err) {
    console.error('Failed to search producers', err)
  } finally {
    loadingProducers.value = false
  }
}
function debouncedSearchProducers() {
  clearTimeout(producerSearchTimer)
  producerSearchTimer = setTimeout(searchProducers, 350)
}

async function handleRoleChange(producer, newRole) {
  const previousRole = producer.role
  producer.role = newRole // optimistic
  try {
    await api.patch(`/admin/producers/${producer.id}/role`, { role: newRole })
    invalidate('/admin/overview')
  } catch (err) {
    producer.role = previousRole
    alert(err.response?.data?.detail || 'Gagal mengubah role')
  }
}

// ---------- Shop items ----------
const shopItems = ref([])
const loadingItems = ref(true)
const showItemForm = ref(false)
const editingItemId = ref(null)
const savingItem = ref(false)
const emptyItemForm = () => ({
  title: '',
  description: '',
  icon: 'shopping_bag',
  color: 'primary',
  category: 'cosmetics',
  cost_diamonds: 0,
  stock: null,
  asset_url: '',
  sort_order: 0,
  active: true,
})
const itemForm = ref(emptyItemForm())

async function loadShopItems({ force = false } = {}) {
  loadingItems.value = true
  try {
    const data = await cachedApiGet('/admin/shop-items', { ttl: 30 * 1000, force })
    shopItems.value = data.items
  } finally {
    loadingItems.value = false
  }
}

function openNewItemForm() {
  editingItemId.value = null
  itemForm.value = emptyItemForm()
  showItemForm.value = true
}

function openEditItemForm(item) {
  editingItemId.value = item.id
  itemForm.value = { ...item }
  showItemForm.value = true
}

function closeItemForm() {
  showItemForm.value = false
  editingItemId.value = null
}

async function handleSaveItem() {
  if (itemForm.value.category === 'avatar' && !itemForm.value.asset_url) {
    alert('Item kategori avatar wajib diisi URL gambarnya')
    return
  }

  savingItem.value = true
  try {
    if (editingItemId.value) {
      await api.patch(`/admin/shop-items/${editingItemId.value}`, itemForm.value)
    } else {
      await api.post('/admin/shop-items', itemForm.value)
    }
    invalidate('/admin/shop-items')
    invalidate('/shop') // supaya halaman Shop producer ikut ke-refresh
    closeItemForm()
    await loadShopItems({ force: true })
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menyimpan item')
  } finally {
    savingItem.value = false
  }
}

// ---------- Idol linking ----------
const idols = ref([])
const loadingIdols = ref(true)
const linkingIdol = ref(null)
const linkQuery = ref('')
const linkCandidates = ref([])
let linkSearchTimer = null

async function loadIdols({ force = false } = {}) {
  loadingIdols.value = true
  try {
    const data = await cachedApiGet('/admin/idols', { ttl: 30 * 1000, force })
    idols.value = data.idols
  } finally {
    loadingIdols.value = false
  }
}

function openLinkModal(idol) {
  linkingIdol.value = idol
  linkQuery.value = ''
  linkCandidates.value = []
}

async function searchLinkCandidates() {
  if (!linkQuery.value) {
    linkCandidates.value = []
    return
  }
  const { data } = await api.get('/admin/producers', { params: { q: linkQuery.value } })
  linkCandidates.value = data.producers
}
function debouncedSearchLinkCandidates() {
  clearTimeout(linkSearchTimer)
  linkSearchTimer = setTimeout(searchLinkCandidates, 350)
}

async function handleLinkIdol(producer) {
  try {
    await api.patch(`/admin/idols/${linkingIdol.value.id}/link`, { producer_id: producer.id })
    invalidate('/admin/idols')
    linkingIdol.value = null
    await loadIdols({ force: true })
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal menautkan akun')
  }
}

async function handleUnlinkIdol(idol) {
  if (!confirm(`Putuskan tautan akun dari "${idol.name}"?`)) return
  try {
    await api.patch(`/admin/idols/${idol.id}/unlink`)
    invalidate('/admin/idols')
    await loadIdols({ force: true })
  } catch (err) {
    alert(err.response?.data?.detail || 'Gagal memutuskan tautan')
  }
}

onMounted(() => {
  loadOverview()
  loadShopItems()
  loadIdols()
})
</script>

<style scoped>
.admin-page { min-height: 100dvh; background: #0d1226; color: #dce1fc; padding-bottom: 48px; }
.top-bar {
  position: fixed; top: 0; left: 0; width: 100%; z-index: 50;
  background: rgba(13, 18, 38, 0.8); backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex; align-items: center; height: 64px; padding: 0 20px;
}
.top-bar h2 { font-size: 16px; font-weight: 700; margin: 0; }
.content {
  max-width: 560px; margin: 0 auto; padding: 96px 20px 48px;
  display: flex; flex-direction: column; gap: 20px;
}

.tabs-row { display: flex; gap: 8px; overflow-x: auto; }
.tab-btn {
  padding: 8px 16px; border-radius: 999px; background: #23293d;
  border: 1px solid rgba(255,255,255,0.05); color: #c3c5d7;
  font-size: 11px; font-weight: 700; letter-spacing: 0.05em; white-space: nowrap; cursor: pointer;
}
.tab-btn.active { background: #b5c4ff; color: #00297a; border-color: transparent; }

.panel { display: flex; flex-direction: column; gap: 16px; }

.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.stat-card {
  border-radius: 16px; padding: 20px; background: rgba(20, 28, 52, 0.8);
  border: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; gap: 4px;
}
.stat-label { font-size: 11px; font-weight: 700; letter-spacing: 0.05em; color: #c3c5d7; }
.stat-value { font-size: 24px; font-weight: 700; color: #b5c4ff; }

.search-input {
  width: 100%; background: #070d20; border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; padding: 12px 16px; color: #dce1fc; font-size: 14px;
}
.search-input:focus { outline: none; border-color: #4f7dff; }

.list { display: flex; flex-direction: column; gap: 8px; }
.row-card {
  display: flex; align-items: center; gap: 12px; padding: 12px;
  border-radius: 12px; background: rgba(20, 28, 52, 0.8); border: 1px solid rgba(255,255,255,0.1);
}
.row-card.inactive { opacity: 0.5; }
.row-avatar { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; background: #191f32; }
.row-info { flex: 1; min-width: 0; }
.row-info h4 { font-size: 13px; font-weight: 700; margin: 0; color: #dce1fc; }
.row-info p { font-size: 11px; color: #c3c5d7; margin: 2px 0 0; }
.cat-tag {
  font-size: 9px; font-weight: 700; text-transform: uppercase; color: #b5c4ff;
  background: rgba(181,196,255,0.1); padding: 1px 6px; border-radius: 999px; margin-left: 6px;
}
.link-status { font-size: 10px; margin-top: 2px; }

.role-select {
  background: #191f32; color: #dce1fc; border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px; padding: 6px 8px; font-size: 12px; font-weight: 700;
}

.item-icon {
  width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.icon-primary { background: rgba(181, 196, 255, 0.1); color: #b5c4ff; }
.icon-secondary { background: rgba(197, 192, 255, 0.2); color: #c5c0ff; }
.icon-tertiary { background: rgba(126, 141, 210, 0.2); color: #b8c4ff; }
.edit-btn {
  background: rgba(255,255,255,0.05); border: none; border-radius: 8px; padding: 8px;
  color: #b5c4ff; cursor: pointer; flex-shrink: 0;
}

.add-btn {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 12px; border-radius: 12px; background: rgba(181,196,255,0.1);
  border: 1px dashed rgba(181,196,255,0.4); color: #b5c4ff; font-weight: 700; font-size: 12px; cursor: pointer;
}

.item-form {
  display: flex; flex-direction: column; gap: 12px; padding: 16px;
  border-radius: 16px; background: rgba(20,28,52,0.8); border: 1px solid rgba(255,255,255,0.1);
}
.item-form h4 { margin: 0; font-size: 14px; }
.field { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: #c3c5d7; }
.field input, .field select {
  background: #070d20; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
  padding: 10px 12px; color: #dce1fc; font-size: 13px;
}
.field-row { display: flex; gap: 12px; }
.field-row .field { flex: 1; }
.checkbox-field { flex-direction: row; align-items: center; gap: 8px; }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; }
.cancel-btn, .save-btn, .link-btn, .unlink-btn {
  padding: 10px 16px; border-radius: 8px; font-size: 12px; font-weight: 700; border: none; cursor: pointer;
}
.cancel-btn { background: rgba(255,255,255,0.05); color: #c3c5d7; }
.cancel-btn.full-width { width: 100%; margin-top: 8px; }
.save-btn { background: #b5c4ff; color: #00297a; }
.save-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.link-btn { background: #b5c4ff; color: #00297a; }
.unlink-btn { background: rgba(255,180,171,0.15); color: #ffb4ab; }

.hint-text { font-size: 12px; color: rgba(195,197,215,0.6); line-height: 1.5; }

.modal-backdrop {
  position: fixed; inset: 0; background: rgba(7,13,32,0.7); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 100; padding: 20px;
}
.modal-card {
  width: 100%; max-width: 400px; background: #151b2e; border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px; padding: 20px; display: flex; flex-direction: column; gap: 12px; max-height: 80vh; overflow-y: auto;
}
.modal-card h4 { margin: 0; font-size: 14px; }
.candidate-row { cursor: pointer; }
.candidate-row:hover { background: rgba(255,255,255,0.05); }
</style>
