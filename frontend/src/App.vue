<script setup>
import { useToast } from "vue-toastification";

const toast = useToast();

const showToast = () => {
  toast.success("This is a success toast!");
  toast.error("This is an error toast!");
  toast.warning("This is a warning toast!");
  toast.info("This is an info toast!");
};
</script>

<template>
  <router-view></router-view>
</template>

<style>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
