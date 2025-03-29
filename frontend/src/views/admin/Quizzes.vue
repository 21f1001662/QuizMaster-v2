<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DataTable from '../../components/DataTable.vue'
import QuizForm from '../../components/QuizForm.vue'
import { useToast } from 'vue-toastification'
import { useRouter } from 'vue-router'

const toast = useToast()
const quizzes = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const showModal = ref(false)
const selectedQuiz = ref(null)
const isEditMode = ref(false)
const router = useRouter()

const columns = [
  { key: 'name', label: 'Name' },
  { 
    key: 'chapter', 
    label: 'Subject',
    formatter: (item) => item.chapter?.subject?.name || '-'
  },
  { 
    key: 'chapter', 
    label: 'Chapter',
    formatter: (item) => item.chapter?.name || '-'
  },
  { 
    key: 'date_of_quiz', 
    label: 'Date',
    formatter: (item) => {
      if (!item.date_of_quiz) return '-'
      const date = new Date(item.date_of_quiz)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    }
  },
  { key: 'duration', label: 'Duration (mins)' },
  { key: 'total_questions', label: 'Questions' },
  { 
    key: 'created_at', 
    label: 'Created At',
    formatter: (item) => {
      if (!item.created_at) return '-'
      const date = new Date(item.created_at)
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    }
  }
]

// Debounce function
const debounce = (fn, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const fetchQuizzes = async (name = '', page = 1) => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get('http://localhost:5000/api/quizzes', {
      params: {
        page: page,
        per_page: 10,
        name: name,
        sort_by: 'created_at',
        sort: 'desc'
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    quizzes.value = response.data.quizzes
    currentPage.value = response.data.current_page
    totalPages.value = response.data.pages
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
  currentPage.value = 1 // Reset to first page on new search
  fetchQuizzes(value, 1)
}, 500)

const handleSearch = (value) => {
  debouncedSearch(value)
}

const handlePageChange = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchQuizzes(searchQuery.value, page)
  }
}

const handleCreate = () => {
  isEditMode.value = false
  selectedQuiz.value = null
  showModal.value = true
}

const handleEdit = (quiz) => {
  isEditMode.value = true
  selectedQuiz.value = quiz
  showModal.value = true
}

const handleDelete = async (quiz) => {
  if (!confirm('Are you sure you want to delete this quiz?')) return

  try {
    const token = localStorage.getItem('adminToken')
    await axios.delete(`http://localhost:5000/api/quizzes/${quiz.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    toast.success('Quiz deleted successfully')
    fetchQuizzes(searchQuery.value, currentPage.value)
  } catch (err) {
    toast.error('Failed to delete quiz')
    console.error(err)
  }
}

const handleSubmit = async (formData) => {
  try {
    const token = localStorage.getItem('adminToken')
    if (isEditMode.value) {
      await axios.put(`http://localhost:5000/api/quizzes/${selectedQuiz.value.id}`, formData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      toast.success('Quiz updated successfully')
    } else {
      await axios.post('http://localhost:5000/api/quizzes', formData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      toast.success('Quiz created successfully')
    }
    showModal.value = false
    fetchQuizzes(searchQuery.value, currentPage.value)
  } catch (err) {
    toast.error(isEditMode.value ? 'Failed to update quiz' : 'Failed to create quiz')
    console.error(err)
  }
}

const handleCloseModal = () => {
  showModal.value = false
  selectedQuiz.value = null
  isEditMode.value = false
}

const handleBuild = (quiz) => {
  router.push(`/admin/dashboard/quizzes/${quiz.id}/build`)
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
      :columns="columns"
      :data="quizzes"
      :loading="loading"
      :error="error"
      v-model:searchQuery="searchQuery"
      :currentPage="currentPage"
      :totalPages="totalPages"
      :showActions="false"
      @row-click="handleBuild"
      @page-change="handlePageChange"
      @search="handleSearch"
    >
      <template #headerActions>
        <button class="btn btn-primary" @click="handleCreate">
          <i class="bi bi-plus-lg me-2"></i>Create New Quiz
        </button>
      </template>
    </DataTable>

    <QuizForm
      :show="showModal"
      :quiz="selectedQuiz"
      :is-edit="isEditMode"
      @close="handleCloseModal"
      @submit="handleSubmit"
    />
  </div>
</template> 