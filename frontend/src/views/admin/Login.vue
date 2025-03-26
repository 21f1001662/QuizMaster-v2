<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from "vue-toastification"
import axios from 'axios'

const router = useRouter()
const toast = useToast()
const username = ref('')
const password = ref('')

const handleLogin = async () => {
  try {
    // Clear student session if exists
    localStorage.removeItem('studentToken')
    localStorage.removeItem('studentUser')

    const response = await axios.post('http://localhost:5000/auth/admin/login', {
      username: username.value,
      password: password.value
    })
    localStorage.setItem('adminToken', response.data.access_token)
    localStorage.setItem('adminUser', JSON.stringify(response.data.user))
    toast.success('Login successful!')
    router.push('/admin/dashboard')
  } catch (error) {
    toast.error('Login failed. Please check your credentials.')
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
      <h2 class="text-3xl font-bold text-center text-gray-900">Admin Login</h2>
      <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
        <div>
          <input v-model="username" type="text" required placeholder="Username"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <div>
          <input v-model="password" type="password" required placeholder="Password"
            class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        </div>
        <button type="submit"
          class="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
          Login
        </button>
      </form>
    </div>
  </div>
</template> 