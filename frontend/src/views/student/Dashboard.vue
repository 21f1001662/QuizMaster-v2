<template>
  <div class="min-vh-100 bg-light">
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
      <div class="container">
        <router-link class="navbar-brand text-primary fw-bold" to="/student/dashboard">
          Student Panel
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
          aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav mx-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/student/dashboard/quizzes" active-class="active">Upcoming Quizzes</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/dashboard/quizzes/completed" active-class="active">Completed Quizzes</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/dashboard/stats" active-class="active">Stats</router-link>
            </li>
          </ul>
          <button @click="handleLogout" class="btn btn-link text-danger p-0" title="Logout">
            <i class="bi bi-box-arrow-right fs-5"></i>
          </button>
        </div>
      </div>
    </nav>

    <main class="container py-4">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('studentToken')
  localStorage.removeItem('studentUser')
  router.push('/student/login')
}

onMounted(() => {
  const token = localStorage.getItem('studentToken')
  if (!token) {
    router.push('/student/login')
  }
})
</script>

<style scoped>
.nav-link.active {
  color: var(--bs-primary) !important;
  font-weight: 500;
}

.btn-link:hover {
  opacity: 0.8;
}
</style> 