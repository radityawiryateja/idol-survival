<template>
  <header class="top-bar">
    <div class="bar-inner">
      <div class="user-info">
        <div class="avatar-wrap">
          <img :src="avatarUrl" alt="" class="avatar" />
          <span class="level-badge">LV.{{ level }}</span>
        </div>
        <div>
          <h1 class="name">{{ name }}</h1>
          <span class="tier">{{ tier }}</span>
        </div>
      </div>
      <div class="actions">
        <button class="icon-btn" aria-label="Notifications">
          <span class="material-symbols-outlined">notifications</span>
        </button>
        <button class="icon-btn" aria-label="Settings">
          <span class="material-symbols-outlined">settings</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  name: { type: String, default: 'Producer' },
  tier: { type: String, default: 'DIAMOND SUPPORTER' },
  level: { type: [String, Number], default: 1 },
  avatarUrl: { type: String, default: '' },
})
</script>

<style scoped>
.top-bar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 50;
  background: rgba(13, 18, 38, 0.8);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.bar-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  padding: 0 20px;
  max-width: 480px;
  margin: 0 auto;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar-wrap {
  position: relative;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(181, 196, 255, 0.3);
  object-fit: cover;
  background: #191f32;
}
.level-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: #b5c4ff;
  color: #00297a;
  font-size: 10px;
  font-weight: 700;
  padding: 0 4px;
  border-radius: 4px;
  border: 1px solid #0d1226;
}
.name {
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
  margin: 0;
  color: #dce1fc;
}
.tier {
  font-size: 11px;
  letter-spacing: 0.05em;
  color: #b5c4ff;
  font-weight: 700;
}
.actions {
  display: flex;
  gap: 8px;
}
.icon-btn {
  background: none;
  border: none;
  padding: 8px;
  border-radius: 12px;
  color: #c3c5d7;
  cursor: pointer;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}
</style>
