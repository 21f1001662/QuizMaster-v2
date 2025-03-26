<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DataTable from '../../components/DataTable.vue'

const quizzes = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'chapter_id', label: 'Chapter ID' },
  { key: 'date_of_quiz', label: 'Date' },
  { key: 'duration', label: 'Duration (mins)' },
  { key: 'total_questions', label: 'Questions' },
  { key: 'remarks', label: 'Remark' }
]

// Debounce function
const debounce = (fn, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const fetchQuizzes = async (name = '') => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get('http://localhost:5000/api/quizzes', {
      params: {
        page: 1,
        per_page: 10,
        name: name
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    quizzes.value = response.data.quizzes
  } catch (err) {
    error.value = 'Failed to fetch quizzes'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Debounced search function
const debouncedSearch = debounce((value) => {
  searchQuery.value = value
  fetchQuizzes(value)
}, 500)

const handleSearch = (value) => {
  debouncedSearch(value)
}

const handleCreate = () => {
  // Implement create functionality
  console.log('Create new quiz')
}

const handleEdit = (quiz) => {
  // Implement edit functionality
  console.log('Edit quiz:', quiz)
}

const handleDelete = (quiz) => {
  // Implement delete functionality
  console.log('Delete quiz:', quiz)
}

onMounted(() => {
  fetchQuizzes()
})
</script>

<template>
  <div>
    <h2 class="mb-4">Quizzes</h2>
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
      :data="quizzes"
      search-placeholder="Search quizzes by name..."
      create-button-text="Create New Quiz"
      v-model="searchQuery"
      @search="handleSearch"
      @create="handleCreate"
      @edit="handleEdit"
      @delete="handleDelete"
    />
  </div>
</template> 