<script setup>
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import { validateAdminToken } from '../utils/auth'

const router = useRouter()

onMounted(async () => {
  const adminToken = localStorage.getItem('adminToken')
  if (adminToken) {
    const isValid = await validateAdminToken(adminToken)
    if (isValid) {
      router.push('/admin/dashboard')
    } else {
      localStorage.removeItem('adminToken')
      localStorage.removeItem('adminUser')
    }
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50">
    <h1 class="text-6xl font-bold text-indigo-600 mb-8">QuizMaster</h1>
  </div>
</template> 