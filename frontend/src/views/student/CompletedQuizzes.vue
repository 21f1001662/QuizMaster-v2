<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'
import debounce from 'lodash/debounce'
import { useRouter } from 'vue-router'

const router = useRouter()
const toast = useToast()

const attempts = ref([])
const subjects = ref([])
const chapters = ref([])
const loading = ref(false)
const subjectsLoading = ref(false)
const chaptersLoading = ref(false)

// Filters
const searchQuery = ref('')
const selectedSubject = ref('')
const selectedChapter = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)
const perPage = ref(10)

// Fetch subjects for filter dropdown
const fetchSubjects = async () => {
  try {
    subjectsLoading.value = true
    const token = localStorage.getItem('studentToken')
    const response = await axios.get('http://localhost:5000/api/subjects', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    subjects.value = response.data.subjects
  } catch (err) {
    toast.error('Failed to fetch subjects')
    console.error(err)
  } finally {
    subjectsLoading.value = false
  }
}

// Fetch chapters for filter dropdown
const fetchChapters = async () => {
  try {
    chaptersLoading.value = true
    const token = localStorage.getItem('studentToken')
    const params = {}
    if (selectedSubject.value) {
      params.subject_id = selectedSubject.value
    }
    const response = await axios.get('http://localhost:5000/api/chapters', {
      headers: {
        Authorization: `Bearer ${token}`
      },
      params
    })
    chapters.value = response.data.chapters
  } catch (err) {
    toast.error('Failed to fetch chapters')
    console.error(err)
  } finally {
    chaptersLoading.value = false
  }
}

// Fetch completed attempts
const fetchAttempts = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('studentToken')
    const params = {
      page: currentPage.value,
      per_page: perPage.value,
      sort_by: 'created_at',
      sort_order: 'desc',
      status: 'completed'
    }

    if (searchQuery.value) params.search = searchQuery.value
    if (selectedSubject.value) params.subject_id = selectedSubject.value
    if (selectedChapter.value) params.chapter_id = selectedChapter.value

    const response = await axios.get('http://localhost:5000/api/attempts', {
      headers: {
        Authorization: `Bearer ${token}`
      },
      params
    })

    attempts.value = response.data.attempts
    currentPage.value = response.data.pagination.page
    totalPages.value = response.data.pagination.total_pages
    totalItems.value = response.data.pagination.total_items
  } catch (err) {
    toast.error('Failed to fetch completed quizzes')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Debounced search function
const debouncedSearch = debounce(() => {
  currentPage.value = 1
  fetchAttempts()
}, 300)

// Watch for filter changes
watch([searchQuery, selectedChapter, selectedSubject], () => {
  if (selectedSubject.value) {
    fetchChapters()
  }
  debouncedSearch()
})

// Format date
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Format duration
const formatDuration = (minutes) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
}

// View responses
const viewResponses = (attemptId) => {
  router.push(`/student/dashboard/quizzes/responses/${attemptId}`)
}

onMounted(() => {
  fetchSubjects()
  fetchChapters()
  fetchAttempts()
})
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Completed Quizzes</h2>
      <span class="badge bg-primary">{{ totalItems }} Attempts</span>
    </div>

    <!-- Main Card -->
    <div class="card">
      <div class="card-body">
        <!-- Filters -->
        <div class="mb-3">
          <div class="row g-3">
            <div class="col-md-4">
              <div class="input-group">
                <span class="input-group-text">
                  <i class="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  class="form-control"
                  v-model="searchQuery"
                  placeholder="Search quizzes..."
                >
              </div>
            </div>
            <div class="col-md-4">
              <div class="position-relative">
                <select class="form-select" v-model="selectedSubject" :disabled="subjectsLoading">
                  <option value="">All Subjects</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
                <div v-if="subjectsLoading" class="position-absolute end-0 top-0 h-100 d-flex align-items-center pe-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="position-relative">
                <select class="form-select" v-model="selectedChapter" :disabled="chaptersLoading || !selectedSubject">
                  <option value="">All Chapters</option>
                  <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                    {{ chapter.name }}
                  </option>
                </select>
                <div v-if="chaptersLoading" class="position-absolute end-0 top-0 h-100 d-flex align-items-center pe-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <!-- Attempts Table -->
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead>
              <tr>
                <th>
                  <i class="bi bi-journal-text me-2"></i>Quiz Name
                </th>
                <th>
                  <i class="bi bi-book me-2"></i>Subject
                </th>
                <th>
                  <i class="bi bi-bookmark me-2"></i>Chapter
                </th>
                <th>
                  <i class="bi bi-calendar-check me-2"></i>Date Attempted
                </th>
                <th>
                  <i class="bi bi-star me-2"></i>Score
                </th>
                <th>
                  <i class="bi bi-gear me-2"></i>Actions
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="attempt in attempts" :key="attempt.id">
                <td>{{ attempt.quiz.name }}</td>
                <td>{{ attempt.quiz.chapter.subject.name }}</td>
                <td>{{ attempt.quiz.chapter.name }}</td>
                <td>{{ formatDate(attempt.completed_at) }}</td>
                <td>
                  <span class="badge" :class="{
                    'bg-success': attempt.score >= attempt.quiz.total_score * 0.7,
                    'bg-warning': attempt.score >= attempt.quiz.total_score * 0.4 && attempt.score < attempt.quiz.total_score * 0.7,
                    'bg-danger': attempt.score < attempt.quiz.total_score * 0.4
                  }">
                    {{ attempt.score }}/{{ attempt.quiz.total_score }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-outline-primary" @click="viewResponses(attempt.id)">
                    <i class="bi bi-eye me-1"></i>View Responses
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- No Results -->
        <div v-if="!loading && attempts.length === 0" class="text-center py-5">
          <i class="bi bi-clipboard-check display-1 text-muted"></i>
          <p class="mt-3">No completed quizzes found</p>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
          <nav>
            <ul class="pagination">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="currentPage--; fetchAttempts()">
                  <i class="bi bi-chevron-left"></i>
                </a>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <a class="page-link" href="#" @click.prevent="currentPage++; fetchAttempts()">
                  <i class="bi bi-chevron-right"></i>
                </a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  background: #fff;
}

.table {
  margin-bottom: 0;
  border-radius: 12px;
  overflow: hidden;
}

.table thead th {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  color: #6c757d;
  font-weight: 600;
  padding: 1rem;
}

.table thead th:first-child {
  border-top-left-radius: 12px;
}

.table thead th:last-child {
  border-top-right-radius: 12px;
}

.table tbody tr:last-child td:first-child {
  border-bottom-left-radius: 12px;
}

.table tbody tr:last-child td:last-child {
  border-bottom-right-radius: 12px;
}

.table tbody td {
  padding: 1rem;
  vertical-align: middle;
  border-bottom: 1px solid #dee2e6;
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.table tbody tr:hover {
  background-color: #f8f9fa;
}

.badge {
  padding: 0.5em 0.8em;
  font-weight: 500;
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.form-control:focus, .form-select:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

.form-select {
  padding-right: 2.5rem;
}

.btn-outline-primary {
  border-radius: 6px;
  padding: 0.4rem 0.8rem;
}

.pagination .page-link {
  border: none;
  padding: 0.5rem 1rem;
  margin: 0 0.25rem;
  border-radius: 6px;
  color: #0d6efd;
}

.pagination .page-item.active .page-link {
  background-color: #0d6efd;
  color: #fff;
}

.pagination .page-item.disabled .page-link {
  color: #6c757d;
  pointer-events: none;
}
</style>