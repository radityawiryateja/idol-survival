<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card">
      <div class="modal-header">
        <h3>Vote untuk {{ idol.name }}</h3>
        <button class="close-btn" @click="$emit('close')" aria-label="Tutup">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div class="balance-row">
        <span class="balance-label">Saldo Vote Tiket Kamu</span>
        <span class="balance-value">{{ balance }}</span>
      </div>

      <div class="stepper-row">
        <button class="step-btn" :disabled="quantity <= 1" @click="quantity--">−</button>
        <span class="quantity-value">{{ quantity }}</span>
        <button class="step-btn" :disabled="quantity >= balance" @click="quantity++">+</button>
      </div>

      <div class="summary-row">
        <span>Total yang dipakai</span>
        <span class="summary-value">{{ quantity }} tiket</span>
      </div>

      <p v-if="quantity > balance" class="error-text">Saldo tiket kamu tidak cukup.</p>

      <button
        class="confirm-btn"
        :disabled="quantity < 1 || quantity > balance || submitting"
        @click="confirm"
      >
        {{ submitting ? 'Memproses...' : `Vote Sekarang (${quantity})` }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  idol: { type: Object, required: true },
  balance: { type: Number, required: true },
})
const emit = defineEmits(['close', 'confirm'])

const quantity = ref(1)
const submitting = ref(false)

async function confirm() {
  submitting.value = true
  await emit('confirm', quantity.value)
  submitting.value = false
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(7, 13, 32, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 100;
}
.modal-card {
  width: 100%;
  max-width: 480px;
  background: #151b2e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px 24px 0 0;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #dce1fc;
  margin: 0;
}
.close-btn {
  background: none;
  border: none;
  color: #c3c5d7;
  cursor: pointer;
}
.balance-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
}
.balance-label { font-size: 13px; color: #c3c5d7; }
.balance-value { font-size: 18px; font-weight: 700; color: #b5c4ff; }
.stepper-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}
.step-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #dce1fc;
  font-size: 20px;
  cursor: pointer;
}
.step-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.quantity-value {
  font-size: 28px;
  font-weight: 700;
  color: #dce1fc;
  min-width: 48px;
  text-align: center;
}
.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #c3c5d7;
}
.summary-value { color: #b5c4ff; font-weight: 700; }
.error-text { color: #ffb4ab; font-size: 12px; margin: 0; }
.confirm-btn {
  padding: 14px;
  border-radius: 12px;
  background: linear-gradient(90deg, #4f7dff, #3d66d6);
  color: #00297a;
  font-weight: 700;
  border: none;
  cursor: pointer;
}
.confirm-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
