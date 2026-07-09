<template>
  <router-view />
  <LoginDialog />
</template>

<script setup lang="ts">
import LoginDialog from './components/LoginDialog.vue'
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  background-color: #f8fafc;
  overflow: hidden;
}
#app {
  height: 100%;
  width: 100%;
}
</style>
