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
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex justify-between h-16">
          <div class="flex space-x-8">
            <h1 class="flex items-center text-xl font-bold text-indigo-600">Admin Panel</h1>
            <div class="flex space-x-4">
              <router-link to="/admin/dashboard/quizzes" class="flex items-center px-3 text-gray-700 hover:text-indigo-600"
                active-class="text-indigo-600">Quizzes</router-link>
              <router-link to="/admin/dashboard/subjects" class="flex items-center px-3 text-gray-700 hover:text-indigo-600"
                active-class="text-indigo-600">Subjects</router-link>
              <router-link to="/admin/dashboard/stats" class="flex items-center px-3 text-gray-700 hover:text-indigo-600"
                active-class="text-indigo-600">Stats</router-link>
            </div>
          </div>
          <button @click="handleLogout"
            class="flex items-center px-4 py-2 text-sm text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
            Logout
          </button>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 px-4">
      <router-view></router-view>
    </main>
  </div>
</template> 