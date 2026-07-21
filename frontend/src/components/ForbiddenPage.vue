<template>
  <div class="forbidden-page">
    <span class="material-symbols-outlined icon">lock</span>
    <h2>Akses Ditolak</h2>
    <p>Kamu tidak punya izin untuk membuka halaman ini.</p>
    <router-link to="/" class="home-link">Kembali ke Home</router-link>
  </div>
</template>

<style scoped>
.forbidden-page {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: #0d1226;
  color: #dce1fc;
  text-align: center;
  padding: 24px;
}
.icon { font-size: 48px; color: #ffb4ab; }
.forbidden-page h2 { margin: 0; font-size: 20px; }
.forbidden-page p { margin: 0; font-size: 13px; color: #c3c5d7; }
.home-link {
  margin-top: 12px;
  color: #b5c4ff;
  font-weight: 700;
  text-decoration: none;
}
</style>
