<template>
  <router-view />
</template>

<script setup>
// Root shell — all page-level layout lives inside each route's component.
</script>

<style>
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  background-color: #0d1226;
}
.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  font-size: 24px;
}
/* Twemoji images injected by src/lib/emoji.js — sized to sit inline with
   surrounding text, same look Telegram Web uses for emoji everywhere. */
.emoji-icon {
  height: 1.2em;
  width: 1.2em;
  vertical-align: -0.2em;
  margin: 0 1px;
}
</style>
