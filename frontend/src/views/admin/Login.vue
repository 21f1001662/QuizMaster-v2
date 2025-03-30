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
    // Clear student session if exists
    localStorage.removeItem('studentToken')
    localStorage.removeItem('studentUser')

    const response = await axios.post('http://localhost:5000/auth/admin/login', {
      username: username.value,
      password: password.value,
    })
    localStorage.setItem('adminToken', response.data.access_token)
    localStorage.setItem('adminUser', JSON.stringify(response.data.user))
    toast.success('Login successful!')
    router.push('/admin/dashboard')
  } catch (error) {
    toast.error('Login failed. Please check your credentials.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="admin-login-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-6 col-lg-4">
          <div class="admin-login-card">
            <div class="text-center mb-4">
              <div class="logo-container">
                <i class="bi bi-shield-lock logo-icon"></i>
                <h1 class="logo-text">Admin Panel</h1>
              </div>
              <p class="text-muted">Please login to access the admin dashboard.</p>
            </div>
            
            <form @submit.prevent="handleLogin" class="admin-login-form">
              <div class="form-group">
                <label for="username" class="form-label">Username</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-person"></i>
                  </span>
                  <input
                    id="username"
                    v-model="username"
                    type="text"
                    class="form-control"
                    required
                    placeholder="Enter your username"
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label for="password" class="form-label">Password</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input
                    id="password"
                    v-model="password"
                    type="password"
                    class="form-control"
                    required
                    placeholder="Enter your password"
                  />
                </div>
              </div>

              <button
                type="submit"
                class="btn btn-dark w-100 admin-login-btn"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                {{ loading ? 'Signing in...' : 'Sign in' }}
              </button>
            </form>

            <div class="text-center mt-4">
              <router-link to="/" class="back-link">
                <i class="bi bi-arrow-left me-1"></i>
                Back to Home
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-login-page {
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
  min-height: 100vh;
}

.admin-login-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.admin-login-card:hover {
  transform: translateY(-5px);
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.logo-icon {
  font-size: 2.5rem;
  color: #2c3e50;
}

.logo-text {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.input-group-text {
  background: #f8f9fa;
  border-right: none;
  color: #6c757d;
}

.form-control {
  border-left: none;
  padding: 0.75rem 1rem;
}

.form-control:focus {
  border-color: #dee2e6;
  box-shadow: none;
}

.input-group:focus-within {
  box-shadow: 0 0 0 0.25rem rgba(44, 62, 80, 0.15);
}

.admin-login-btn {
  padding: 0.75rem;
  font-weight: 500;
  border-radius: 8px;
  background: #2c3e50;
  border: none;
  transition: all 0.3s ease;
}

.admin-login-btn:hover {
  background: #1a1a1a;
  transform: translateY(-2px);
}

.admin-login-btn:disabled {
  background: #6c757d;
  transform: none;
}

.back-link {
  color: #6c757d;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-link:hover {
  color: #2c3e50;
  transform: translateX(-5px);
}

.spinner-border {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}
</style> 