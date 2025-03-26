<script setup>
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'
import { validateAdminToken, validateStudentToken } from '../utils/auth'

const router = useRouter()

onMounted(async () => {
  // Check for admin token
  const adminToken = localStorage.getItem('adminToken')
  if (adminToken) {
    const isValid = await validateAdminToken(adminToken)
    if (isValid) {
      router.push('/admin/dashboard')
      return
    } else {
      localStorage.removeItem('adminToken')
      localStorage.removeItem('adminUser')
    }
  }

  // Check for student token
  const studentToken = localStorage.getItem('studentToken')
  if (studentToken) {
    const isValid = await validateStudentToken(studentToken)
    if (isValid) {
      router.push('/student/dashboard/quizzes')
    } else {
      localStorage.removeItem('studentToken')
      localStorage.removeItem('studentUser')
    }
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50">
    <h1 class="text-6xl font-bold text-indigo-600 mb-8">QuizMaster</h1>
    <div class="space-y-4">
      <router-link
        to="/admin/login"
        class="block w-full px-4 py-2 text-center text-white bg-indigo-600 rounded-md hover:bg-indigo-700"
      >
        Admin Login
      </router-link>
      <router-link
        to="/student/login"
        class="block w-full px-4 py-2 text-center text-white bg-green-600 rounded-md hover:bg-green-700"
      >
        Student Login
      </router-link>
    </div>
  </div>
</template> 