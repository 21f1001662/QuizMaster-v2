<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DataTable from '../../components/DataTable.vue'
import SubjectForm from '../../components/SubjectForm.vue'
import { useToast } from 'vue-toastification'

const toast = useToast()
const subjects = ref([])
const loading = ref(false)
const error = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const showModal = ref(false)
const selectedSubject = ref(null)
const isEditMode = ref(false)

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'description', label: 'Description' },
  { key: 'created_at', label: 'Created At' }
]

// Debounce function
const debounce = (fn, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const fetchSubjects = async (search = '', page = 1) => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get('http://localhost:5000/api/subjects', {
      params: {
        page: page,
        per_page: 10,
        search: search,
        sort_by: 'created_at',
        sort: 'desc'
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    subjects.value = response.data.subjects
    currentPage.value = response.data.current_page
    totalPages.value = response.data.pages
  } catch (err) {
    error.value = 'Failed to fetch subjects'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Debounced search function
const debouncedSearch = debounce((value) => {
  searchQuery.value = value
  currentPage.value = 1 // Reset to first page on new search
  fetchSubjects(value, 1)
}, 500)

const handleSearch = (value) => {
  debouncedSearch(value)
}

const handlePageChange = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    fetchSubjects(searchQuery.value, page)
  }
}

const handleCreate = () => {
  isEditMode.value = false
  selectedSubject.value = null
  showModal.value = true
}

const handleEdit = (subject) => {
  isEditMode.value = true
  selectedSubject.value = subject
  showModal.value = true
}

const handleDelete = async (subject) => {
  if (!confirm('Are you sure you want to delete this subject?')) return

  try {
    const token = localStorage.getItem('adminToken')
    await axios.delete(`http://localhost:5000/api/subjects/${subject.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    toast.success('Subject deleted successfully')
    fetchSubjects(searchQuery.value, currentPage.value)
  } catch (err) {
    toast.error('Failed to delete subject')
    console.error(err)
  }
}

const handleSubmit = async (formData) => {
  try {
    const token = localStorage.getItem('adminToken')
    if (isEditMode.value) {
      await axios.put(`http://localhost:5000/api/subjects/${selectedSubject.value.id}`, formData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      toast.success('Subject updated successfully')
    } else {
      await axios.post('http://localhost:5000/api/subjects', formData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      toast.success('Subject created successfully')
    }
    showModal.value = false
    fetchSubjects(searchQuery.value, currentPage.value)
  } catch (err) {
    toast.error(isEditMode.value ? 'Failed to update subject' : 'Failed to create subject')
    console.error(err)
  }
}

const handleCloseModal = () => {
  showModal.value = false
  selectedSubject.value = null
  isEditMode.value = false
}

onMounted(() => {
  fetchSubjects()
})
</script>

<template>
  <div>
    <h2 class="mb-4">Subjects</h2>
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
      :data="subjects"
      search-placeholder="Search subjects by name..."
      create-button-text="Create New Subject"
      v-model="searchQuery"
      :current-page="currentPage"
      :total-pages="totalPages"
      @search="handleSearch"
      @create="handleCreate"
      @edit="handleEdit"
      @delete="handleDelete"
      @page-change="handlePageChange"
    />

    <SubjectForm
      :show="showModal"
      :subject="selectedSubject"
      :is-edit="isEditMode"
      @close="handleCloseModal"
      @submit="handleSubmit"
    />
  </div>
</template>