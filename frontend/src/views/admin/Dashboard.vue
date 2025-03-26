<script setup>
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('adminToken')
  localStorage.removeItem('adminUser')
  router.push('/admin/login')
}

onMounted(() => {
  const token = localStorage.getItem('adminToken')
  if (!token) {
    router.push('/admin/login')
  }
})
</script>

<template>
  <div class="min-vh-100 bg-light">
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
      <div class="container">
        <router-link class="navbar-brand text-primary fw-bold" to="/admin/dashboard">
          Admin Panel
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
          aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav mx-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard/quizzes" active-class="active">Quizzes</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard/subjects" active-class="active">Subjects</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard/chapters" active-class="active">Chapters</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/dashboard/stats" active-class="active">Stats</router-link>
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

<style scoped>
.nav-link.active {
  color: var(--bs-primary) !important;
  font-weight: 500;
}

.btn-link:hover {
  opacity: 0.8;
}
</style> 