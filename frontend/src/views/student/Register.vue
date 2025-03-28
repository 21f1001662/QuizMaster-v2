<template>
  <div class="container">
    <div class="row justify-content-center align-items-center min-vh-100">
      <div class="col-md-6 col-lg-4">
        <div class="card shadow">
          <div class="card-body p-4">
            <h2 class="text-center mb-4">Student Registration</h2>
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input
                  id="username"
                  v-model="formData.username"
                  type="text"
                  class="form-control"
                  required
                  placeholder="Choose a username"
                />
              </div>
              <div class="mb-3">
                <label for="full_name" class="form-label">Full Name</label>
                <input
                  id="full_name"
                  v-model="formData.full_name"
                  type="text"
                  class="form-control"
                  required
                  placeholder="Enter your full name"
                />
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input
                  id="password"
                  v-model="formData.password"
                  type="password"
                  class="form-control"
                  required
                  placeholder="Choose a password"
                />
              </div>
              <div class="mb-3">
                <label for="dob" class="form-label">Date of Birth</label>
                <input
                  id="dob"
                  v-model="formData.dob"
                  type="date"
                  class="form-control"
                  required
                />
              </div>
              <button
                type="submit"
                class="btn btn-success w-100"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
            </form>
            <div class="text-center mt-3">
              Already have an account? <router-link to="/student/login">Login here</router-link>
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
const loading = ref(false)

const formData = ref({
  username: '',
  password: '',
  full_name: '',
  dob: '',
  qualification: 'student'
})

const handleRegister = async () => {
  try {
    loading.value = true
    const response = await axios.post('http://localhost:5000/auth/register', formData.value)
    localStorage.setItem('studentToken', response.data.access_token)
    localStorage.setItem('studentUser', JSON.stringify(response.data.user))
    toast.success('Registration successful!')
    router.push('/student/dashboard/quizzes')
  } catch (error) {
    toast.error(error.response?.data?.message || 'Registration failed. Please try again.')
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