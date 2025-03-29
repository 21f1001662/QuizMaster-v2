<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import DataTable from '../../components/DataTable.vue'

const toast = useToast()

const students = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const searchTimeout = ref(null)

const columns = [
  { 
    key: 'full_name', 
    label: 'Name',
    icon: 'bi bi-person'
  },
  { 
    key: 'username', 
    label: 'Username',
    icon: 'bi bi-person-circle'
  },
  { 
    key: 'qualification', 
    label: 'Qualification',
    icon: 'bi bi-mortarboard',
    formatter: (item) => item.qualification || '-'
  },
  { 
    key: 'dob', 
    label: 'Date of Birth',
    icon: 'bi bi-calendar-heart',
    formatter: (item) => {
      if (!item.dob) return '-'
      const date = new Date(item.dob)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }
  },
  { 
    key: 'created_at', 
    label: 'Registered On',
    icon: 'bi bi-calendar-check',
    formatter: (item) => {
      if (!item.created_at) return '-'
      const date = new Date(item.created_at)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }
  }
]

const fetchStudents = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get('http://localhost:5000/user/users', {
      params: {
        search: searchQuery.value,
        page: currentPage.value,
        per_page: 10,
        sort_by: 'created_at',
        sort: 'desc'
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    students.value = response.data.users
    currentPage.value = response.data.current_page
    totalPages.value = response.data.pages
  } catch (err) {
    error.value = 'Failed to fetch students'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = (query) => {
  searchQuery.value = query
  currentPage.value = 1
  
  // Clear existing timeout
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  // Set new timeout
  searchTimeout.value = setTimeout(() => {
    fetchStudents()
  }, 300) // 300ms delay
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchStudents()
}

onMounted(() => {
  fetchStudents()
})
</script>

<template>
  <div>
    <h2 class="mb-4">Students</h2>
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <DataTable
      v-else
      :columns="columns"
      :data="students"
      search-placeholder="Search students by name or username..."
      :current-page="currentPage"
      :total-pages="totalPages"
      v-model="searchQuery"
      @search="handleSearch"
      @page-change="handlePageChange"
      :show-create-button="false"
      :show-actions="false"
    />
  </div>
</template> 