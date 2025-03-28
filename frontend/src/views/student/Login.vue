<template>
  <div class="container">
    <div class="row justify-content-center align-items-center min-vh-100">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-body p-4">
            <h2 class="text-center mb-4">Student Login</h2>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input
                  id="username"
                  v-model="username"
                  type="text"
                  class="form-control"
                  required
                  placeholder="Enter your username"
                />
              </div>
              <div class="mb-4">
                <label for="password" class="form-label">Password</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  required
                  placeholder="Enter your password"
                />
              </div>
              <button
                type="submit"
                class="btn btn-success w-100"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                {{ loading ? 'Signing in...' : 'Sign in' }}
              </button>
            </form>
            <div class="text-center mt-3">
              New user? <router-link to="/student/register">Register here</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from "vue-toastification"
import axios from 'axios'

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

    const response = await axios.post('http://localhost:5000/auth/login', {
      username: username.value,
      password: password.value,
    })
    localStorage.setItem('studentToken', response.data.access_token)
    localStorage.setItem('studentUser', JSON.stringify(response.data.user))
    toast.success('Login successful!')
    router.push('/student/dashboard/quizzes')
  } catch (error) {
    toast.error('Login failed. Please check your credentials.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}

.spinner-border {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 0.2em solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border .75s linear infinite;
}

.me-2 {
  margin-right: 0.5rem;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}
</style> 