<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'
import debounce from 'lodash/debounce'
import { useRouter } from 'vue-router'

const router = useRouter()
const toast = useToast()
const quizzes = ref([])
const chapters = ref([])
const subjects = ref([])
const loading = ref(false)
const chaptersLoading = ref(false)
const subjectsLoading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalQuizzes = ref(0)

// Filters
const searchQuery = ref('')
const selectedChapter = ref('')
const selectedSubject = ref('')
const perPage = ref(20)

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

// Fetch quizzes with filters
const fetchQuizzes = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('studentToken')
    const params = {
      page: currentPage.value,
      per_page: perPage.value,
      sort_by: 'date_of_quiz',
      sort: 'DESC',
      date_lb: new Date().toISOString().split('T')[0], // Only show future quizzes
      date_ub: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0]
    }

    if (searchQuery.value) params.name = searchQuery.value
    if (selectedChapter.value) params.chapter_id = selectedChapter.value
    if (selectedSubject.value) params.subject_id = selectedSubject.value

    const response = await axios.get('http://localhost:5000/api/student/quizzes', {
      headers: {
        Authorization: `Bearer ${token}`
      },
      params
    })

    quizzes.value = response.data.quizzes
    currentPage.value = response.data.current_page
    totalPages.value = response.data.pages
    totalQuizzes.value = response.data.total
  } catch (err) {
    toast.error('Failed to fetch quizzes')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Debounced search function
const debouncedSearch = debounce(() => {
  currentPage.value = 1
  fetchQuizzes()
}, 300)

// Watch for filter changes
watch([searchQuery, selectedChapter, selectedSubject], () => {
  if (selectedSubject.value) {
    fetchChapters()
  }
  debouncedSearch()
})

// Start quiz
const startQuiz = (quizId) => {
  router.push(`/student/dashboard/quizzes/${quizId}/attempt`)
}

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
  const days = Math.floor(minutes / (24 * 60))
  const hours = Math.floor((minutes % (24 * 60)) / 60)
  const mins = minutes % 60

  if (days > 0) {
    return `${days}d ${hours}h ${mins}m`
  } else if (hours > 0) {
    return `${hours}h ${mins}m`
  } else {
    return `${mins}m`
  }
}

// Get subject display name
const getSubjectDisplayName = (chapterId) => {
  const chapter = chapters.value.find(c => c.id === chapterId)
  if (!chapter) return ''
  return chapter.subject.name
}

onMounted(() => {
  fetchSubjects()
  fetchChapters()
  fetchQuizzes()
})
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Upcoming Quizzes</h2>
      <span class="badge bg-primary">{{ totalQuizzes }} Quizzes</span>
    </div>
    
    <!-- Filters -->
    <div class="row mb-4 g-3">
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
      <div class="col-md-4">
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

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Quizzes Grid -->
    <div v-else class="row g-4">
      <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-6 col-lg-4">
        <div class="card h-100 shadow-sm hover-shadow">
          <div class="card-body d-flex flex-column">
            <div class="mb-3">
              <h5 class="card-title mb-1">{{ quiz.name }}</h5>
              <span class="text-primary badge bg-light ms-0">{{ getSubjectDisplayName(quiz.chapter_id) }}</span>
            </div>
            <p class="card-text text-muted small mb-4 description">{{ quiz.instructions }}</p>
            
            <div class="quiz-info mt-auto">
              <div class="d-flex align-items-center mb-2">
                <i class="bi bi-calendar-event me-2 text-primary"></i>
                <span>{{ formatDate(quiz.date_of_quiz) }}</span>
              </div>
              
              <div class="d-flex align-items-center mb-2">
                <i class="bi bi-clock me-2 text-primary"></i>
                <span>{{ formatDuration(quiz.duration) }}</span>
              </div>
              
              <div class="d-flex align-items-center mb-4">
                <i class="bi bi-question-circle me-2 text-primary"></i>
                <span>{{ quiz.total_questions }} Questions</span>
              </div>

              <button 
                class="btn btn-primary w-100"
                @click="startQuiz(quiz.id)"
              >
                Start Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="!loading && quizzes.length === 0" class="text-center py-5">
      <i class="bi bi-calendar-x display-1 text-muted"></i>
      <p class="mt-3">No upcoming quizzes found</p>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
      <nav>
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="currentPage--; fetchQuizzes()">Previous</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="currentPage++; fetchQuizzes()">Next</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.hover-shadow {
  transition: all 0.3s ease;
}

.hover-shadow:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.card {
  border: none;
  border-radius: 12px;
  background: #fff;
  overflow: hidden;
}

.card-body {
  padding: 1.5rem;
  height: 100%;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
}

.badge {
  font-size: 0.75rem;
  padding: 0.5em 0.8em;
  font-weight: 500;
  margin-left: 0 !important;
}

.btn-primary {
  border-radius: 8px;
  padding: 0.6rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(13, 110, 253, 0.2);
}

.input-group-text, .form-control, .form-select {
  border-radius: 12px;
  border: 1px solid #e0e0e0;
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

.description {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.quiz-info {
  border-top: 1px solid #f0f0f0;
  padding-top: 1rem;
  margin-top: auto;
}

.bi {
  font-size: 1.1rem;
}

.text-muted {
  color: #6c757d !important;
}
</style> 