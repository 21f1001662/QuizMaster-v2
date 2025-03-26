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
  <div class="container">
    <div class="row justify-content-center align-items-center min-vh-100">
      <div class="col-md-6 text-center">
        <h1 class="display-4 text-primary mb-4">QuizMaster</h1>
        <div class="d-grid gap-3">
          <router-link
            to="/admin/login"
            class="btn btn-primary btn-lg"
          >
            Admin Login
          </router-link>
          <router-link
            to="/student/login"
            class="btn btn-success btn-lg"
          >
            Student Login
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}
</style> 