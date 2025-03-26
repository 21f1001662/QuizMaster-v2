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
  <div class="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">

    <h1 class="text-3xl font-bold text-center mb-8 text-indigo-600">Vue.js</h1>
    <p class="text-center mb-8">Test toast notifications!</p>
    <button @click="showToast"
      class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
      Show Toasts
    </button>
  </div>
</template>

<style scoped>
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
