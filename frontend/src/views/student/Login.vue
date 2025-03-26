<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Student Login
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">Username</label>
            <input
              id="username"
              v-model="username"
              name="username"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Username"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Signing in...</span>
            <span v-else>Sign in</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from "vue-toastification"

export default {
  name: 'StudentLogin',
  setup() {
    const router = useRouter()
    const toast = useToast()
    const username = ref('')
    const password = ref('')
    const loading = ref(false)

    const handleLogin = async () => {
      try {
        loading.value = true

        // Clear admin session if exists
        localStorage.removeItem('adminToken')
        localStorage.removeItem('adminUser')

        const response = await fetch('http://localhost:5000/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: username.value,
            password: password.value
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.detail || 'Login failed')
        }

        // Store the token and user data
        localStorage.setItem('studentToken', data.access_token)
        localStorage.setItem('studentUser', JSON.stringify(data.user))
        
        toast.success('Login successful!')
        router.push('/student/dashboard/quizzes')
      } catch (err) {
        toast.error(err.message || 'Login failed. Please check your credentials.')
        console.error('Login failed:', err)
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      loading,
      handleLogin
    }
  }
}
</script> 