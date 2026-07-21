<template>
  <div class="avatar-frame" :class="`frame-${frameStyle || 'none'}`" :style="{ width: size + 'px', height: size + 'px' }">
    <div class="avatar-frame-inner">
      <img :src="avatarUrl" :alt="alt" class="avatar-frame-img" />
    </div>
    <img v-if="frameAssetUrl" :src="frameAssetUrl" class="avatar-frame-overlay" alt="" />
    <template v-if="frameStyle === 'legendary_particles'">
      <span class="particle p1" :style="{ '--r': orbitRadius + 'px' }"></span>
      <span class="particle p2" :style="{ '--r': orbitRadius + 'px' }"></span>
      <span class="particle p3" :style="{ '--r': orbitRadius + 'px' }"></span>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  avatarUrl: { type: String, default: '' },
  frameStyle: { type: String, default: 'none' },
  frameAssetUrl: { type: String, default: '' },
  size: { type: Number, default: 64 },
  alt: { type: String, default: '' },
})

const orbitRadius = computed(() => props.size / 2 - 4)
</script>

<style scoped>
.avatar-frame {
  position: relative;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.avatar-frame-inner {
  width: 86%;
  height: 86%;
  border-radius: 50%;
  overflow: hidden;
  background: #191f32;
  position: relative;
  z-index: 2;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.avatar-frame-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-frame-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 3;
  pointer-events: none;
  object-fit: contain;
}

.frame-none .avatar-frame-inner { border: 2px solid rgba(255, 255, 255, 0.1); }

.frame-bronze_shine::before {
  content: ''; position: absolute; inset: -3px; border-radius: 50%; z-index: 1;
  background: linear-gradient(135deg, #cd7f32, #f0c090, #cd7f32);
  animation: frame-shine 3s linear infinite;
}
.frame-silver_pulse::before {
  content: ''; position: absolute; inset: -3px; border-radius: 50%; z-index: 1;
  background: conic-gradient(from 0deg, #c9d6ff, #e2e2e2, #c9d6ff);
  animation: frame-spin 4s linear infinite;
  box-shadow: 0 0 12px rgba(201, 214, 255, 0.6);
}
.frame-gold_glow::before {
  content: ''; position: absolute; inset: -3px; border-radius: 50%; z-index: 1;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  box-shadow: 0 0 16px rgba(255, 215, 0, 0.7);
  animation: frame-pulse 2s ease-in-out infinite;
}
.frame-epic_rotate::before {
  content: ''; position: absolute; inset: -4px; border-radius: 50%; z-index: 1;
  background: conic-gradient(from 0deg, #a855f7, #4f7dff, #a855f7);
  animation: frame-spin 3s linear infinite;
  box-shadow: 0 0 18px rgba(168, 85, 247, 0.6);
}
.frame-legendary_particles::before {
  content: ''; position: absolute; inset: -4px; border-radius: 50%; z-index: 1;
  background: conic-gradient(from 0deg, #ff4d4d, #ffd700, #4f7dff, #ff4d4d);
  animation: frame-spin 2.5s linear infinite;
  box-shadow: 0 0 24px rgba(255, 215, 0, 0.8);
}
.particle {
  position: absolute; top: 50%; left: 50%; width: 6px; height: 6px;
  margin: -3px; border-radius: 50%; z-index: 4;
  background: #ffd700; box-shadow: 0 0 6px #ffd700;
  animation: particle-orbit 2.4s linear infinite;
}
.particle.p2 { animation-delay: -0.8s; background: #4f7dff; box-shadow: 0 0 6px #4f7dff; }
.particle.p3 { animation-delay: -1.6s; background: #ff4d4d; box-shadow: 0 0 6px #ff4d4d; }

@keyframes frame-spin { to { transform: rotate(360deg); } }
@keyframes frame-shine { 0%, 100% { filter: brightness(1); } 50% { filter: brightness(1.3); } }
@keyframes frame-pulse {
  0%, 100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
  50% { box-shadow: 0 0 22px rgba(255, 215, 0, 0.9); }
}
@keyframes particle-orbit {
  from { transform: rotate(0deg) translateX(var(--r, 34px)) rotate(0deg); }
  to { transform: rotate(360deg) translateX(var(--r, 34px)) rotate(-360deg); }
}
</style>
