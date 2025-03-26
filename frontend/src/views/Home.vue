<script setup>
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const router = useRouter()

onMounted(() => {
  const adminToken = localStorage.getItem('adminToken')
  if (adminToken) {
    router.push('/admin/dashboard')
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50">
    <h1 class="text-6xl font-bold text-indigo-600 mb-8">QuizMaster</h1>
  </div>
</template> 