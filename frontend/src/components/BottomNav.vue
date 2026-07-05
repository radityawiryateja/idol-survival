<template>
  <nav class="bottom-nav">
    <router-link
      v-for="item in items"
      :key="item.name"
      :to="item.to"
      class="nav-item"
      :class="{ active: route.path === item.to }"
    >
      <span class="material-symbols-outlined">{{ item.icon }}</span>
      <span class="nav-label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { name: 'home', to: '/', icon: 'dashboard', label: 'Home' },
  { name: 'idols', to: '/idols', icon: 'groups', label: 'Idols' },
  { name: 'tasks', to: '/tasks', icon: 'assignment', label: 'Tasks' },
  { name: 'vote', to: '/vote', icon: 'how_to_reg', label: 'Vote' },
  { name: 'profile', to: '/profile', icon: 'account_circle', label: 'Profile' },
]
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  z-index: 50;
  background: rgba(25, 31, 50, 0.9);
  backdrop-filter: blur(24px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 8px 16px 24px;
  max-width: 480px;
  margin: 0 auto;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: rgba(220, 225, 252, 0.6);
  text-decoration: none;
  transition: all 0.2s;
}
.nav-item.active {
  background: rgba(181, 196, 255, 0.1);
  color: #b5c4ff;
  border-radius: 12px;
  padding: 4px 12px;
  transform: scale(0.9);
}
.nav-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-top: 4px;
}
</style>
