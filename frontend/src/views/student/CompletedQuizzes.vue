<script setup>
import { ref, onMounted, watch, computed } from 'vue'
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

// Add new refs for responses popup
const showResponsesPopup = ref(false)
const selectedAttempt = ref(null)
const responsesLoading = ref(false)

// Add computed properties for response summary
const responseSummary = computed(() => {
  if (!selectedAttempt.value?.responses) return null

  const responses = selectedAttempt.value.responses
  const total = responses.length
  const correct = responses.filter(r => r.is_correct).length
  const incorrect = responses.filter(r => !r.is_correct && r.is_attempted).length
  const notAttempted = responses.filter(r => !r.is_attempted).length

  const correctMarks = responses.reduce((sum, r) => sum + (r.is_correct ? r.question.details.correct_marks : 0), 0)
  const incorrectMarks = responses.reduce((sum, r) => sum + (!r.is_correct && r.is_attempted ? r.question.details.incorrect_marks : 0), 0)

  return {
    total,
    correct,
    incorrect,
    notAttempted,
    correctMarks,
    incorrectMarks
  }
})

// Add computed property for score percentage
const scorePercentage = computed(() => {
  if (!selectedAttempt.value) return 0
  return (selectedAttempt.value.score / selectedAttempt.value.quiz.total_score) * 100
})

// Add computed property for score color
const scoreColor = computed(() => {
  if (scorePercentage.value < 35) return '#dc3545' // red
  if (scorePercentage.value < 70) return '#ffc107' // yellow
  return '#198754' // green
})

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

// Update viewResponses function
const viewResponses = async (attemptId) => {
  try {
    responsesLoading.value = true
    const token = localStorage.getItem('studentToken')
    const response = await axios.get(`http://localhost:5000/api/attempts/${attemptId}/responses`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    selectedAttempt.value = response.data
    showResponsesPopup.value = true
  } catch (err) {
    toast.error('Failed to fetch responses')
    console.error(err)
  } finally {
    responsesLoading.value = false
  }
}

// Add helper functions for responses
const getOptionLetter = (index) => {
  return String.fromCharCode(65 + index)
}

const formatNumericAnswer = (value) => {
  return Number(value).toFixed(2)
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

    <!-- Responses Popup -->
    <div v-if="showResponsesPopup" class="modal-backdrop show" style="display: block;"></div>
    <div v-if="showResponsesPopup" class="modal show" style="display: block;">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content responses-modal">
          <div class="modal-header border-0">
            <h5 class="modal-title">Quiz Responses</h5>
            <button type="button" class="btn-close" @click="showResponsesPopup = false"></button>
          </div>
          
          <div class="modal-body">
            <!-- Loading State -->
            <div v-if="responsesLoading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <!-- Responses Content -->
            <div v-else>
              <!-- Score Summary -->
              <div class="score-summary mb-4">
                <div class="d-flex align-items-center justify-content-between">
                  <div>
                    <h6 class="mb-1">Final Score</h6>
                    <div class="score-value" :style="{ color: scoreColor }">
                      {{ selectedAttempt?.score }} / {{ selectedAttempt?.quiz.total_score }}
                    </div>
                  </div>
                  <div class="text-end">
                    <h6 class="mb-1">Completion Date</h6>
                    <div class="text-muted">{{ formatDate(selectedAttempt?.completed_at) }}</div>
                  </div>
                </div>
              </div>

              <!-- Response Summary -->
              <div class="response-summary mb-4">
                <div class="row g-3">
                  <div class="col-md-4">
                    <div class="summary-card correct">
                      <div class="summary-icon">✅</div>
                      <div class="summary-content">
                        <div class="summary-label">Correct</div>
                        <div class="summary-value">{{ responseSummary?.correct }}/{{ responseSummary?.total }}</div>
                        <div class="summary-marks">+{{ responseSummary?.correctMarks }} marks</div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="summary-card incorrect">
                      <div class="summary-icon">❌</div>
                      <div class="summary-content">
                        <div class="summary-label">Incorrect</div>
                        <div class="summary-value">{{ responseSummary?.incorrect }}/{{ responseSummary?.total }}</div>
                        <div class="summary-marks">{{ responseSummary?.incorrectMarks }} marks</div>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="summary-card not-attempted">
                      <div class="summary-icon">⏭️</div>
                      <div class="summary-content">
                        <div class="summary-label">Not Attempted</div>
                        <div class="summary-value">{{ responseSummary?.notAttempted }}/{{ responseSummary?.total }}</div>
                        <div class="summary-marks">0 marks</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Questions List -->
              <div class="questions-list">
                <div v-for="(response, index) in selectedAttempt?.responses" :key="response.id" class="question-card mb-4">
                  <!-- Question Status Badge -->
                  <div class="question-status" :class="{
                    'correct': response.is_correct,
                    'incorrect': !response.is_correct && response.is_attempted,
                    'not-attempted': !response.is_attempted
                  }">
                    <i :class="{
                      'bi bi-check-circle-fill': response.is_correct,
                      'bi bi-x-circle-fill': !response.is_correct && response.is_attempted,
                      'bi bi-dash-circle-fill': !response.is_attempted
                    }"></i>
                    {{ response.is_correct ? 'Correct' : (!response.is_attempted ? 'Not Attempted' : 'Incorrect') }}
                  </div>

                  <!-- Question Header -->
                  <div class="question-header">
                    <div class="question-number">Question {{ index + 1 }}</div>
                    <div class="question-marks" :class="{
                      'correct': response.is_correct,
                      'incorrect': !response.is_correct && response.is_attempted,
                      'not-attempted': !response.is_attempted
                    }">
                      {{ response.is_correct ? '+' + response.question.details.correct_marks : 
                         (!response.is_attempted ? '0' : response.question.details.incorrect_marks) }} marks
                    </div>
                  </div>

                  <!-- Question Text -->
                  <div class="question-text">
                    {{ response.question.details.question_text }}
                  </div>

                  <!-- MCQ Options -->
                  <div v-if="response.question.type === 'mcq'" class="options-list">
                    <div
                      v-for="(option, optIndex) in response.question.details.options"
                      :key="option.id"
                      class="option-item"
                      :class="{
                        'selected': response.answer.option_id === option.id,
                        'correct': option.is_correct,
                        'incorrect': response.answer.option_id === option.id && !option.is_correct
                      }"
                    >
                      <div class="option-circle">
                        {{ getOptionLetter(optIndex) }}
                      </div>
                      <div class="option-text">{{ option.text }}</div>
                      <div class="option-status ms-auto">
                        <i v-if="option.is_correct" class="bi bi-check-circle-fill text-success"></i>
                        <i v-else-if="response.answer.option_id === option.id" class="bi bi-x-circle-fill text-danger"></i>
                      </div>
                    </div>
                  </div>

                  <!-- Numeric Answer -->
                  <div v-else class="numeric-answer">
                    <div class="answer-box">
                      <div class="answer-label">Your Answer</div>
                      <div class="answer-value">{{ formatNumericAnswer(response.answer.value) }}</div>
                    </div>
                    <div class="answer-range">
                      <div class="range-label">Correct Range</div>
                      <div class="range-value">
                        {{ formatNumericAnswer(response.question.details.answer_lower_bound) }} - 
                        {{ formatNumericAnswer(response.question.details.answer_upper_bound) }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer border-0">
            <button type="button" class="btn btn-secondary" @click="showResponsesPopup = false">Close</button>
          </div>
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

.responses-modal {
  border: none;
  border-radius: 16px;
  background: #fff;
}

.modal-header {
  padding: 1.5rem;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
}

.score-summary {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
}

.score-value {
  font-size: 2rem;
  font-weight: 600;
  transition: color 0.3s ease;
}

.question-card {
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
  transition: all 0.3s ease;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.question-status {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.question-status.correct {
  background: #e8f5e9;
  color: #198754;
}

.question-status.incorrect {
  background: #fce8e8;
  color: #dc3545;
}

.question-status.not-attempted {
  background: #e9ecef;
  color: #6c757d;
}

.question-header {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-right: 120px;
}

.question-number {
  background: #f8f9fa;
  color: #6c757d;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  margin-right: 1rem;
}

.question-marks {
  font-size: 1.1rem;
  font-weight: 600;
}

.question-marks.correct {
  color: #198754;
}

.question-marks.incorrect {
  color: #dc3545;
}

.question-marks.not-attempted {
  color: #6c757d;
}

.question-text {
  font-size: 1.1rem;
  color: #2c3e50;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.option-item.selected {
  border-color: #0d6efd;
  background: #e7f1ff;
}

.option-item.correct {
  border-color: #198754;
  background: #e8f5e9;
}

.option-item.incorrect {
  border-color: #dc3545;
  background: #fce8e8;
}

.option-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-weight: 500;
}

.option-item.selected .option-circle {
  background: #0d6efd;
  color: #fff;
}

.option-item.correct .option-circle {
  background: #198754;
  color: #fff;
}

.option-item.incorrect .option-circle {
  background: #dc3545;
  color: #fff;
}

.option-text {
  flex: 1;
}

.option-status {
  font-size: 1.2rem;
}

.numeric-answer {
  display: flex;
  gap: 1.5rem;
}

.answer-box, .answer-range {
  flex: 1;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.answer-label, .range-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.answer-value {
  font-size: 1.25rem;
  font-weight: 500;
  color: #2c3e50;
}

.range-value {
  font-size: 1.25rem;
  font-weight: 500;
  color: #198754;
}

.btn-close {
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.btn-close:hover {
  opacity: 1;
}

.response-summary {
  margin-top: 1.5rem;
}

.summary-card {
  background: #fff;
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  position: relative;
}

.summary-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 70%;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  transition: all 0.3s ease;
}

.summary-card:hover::before {
  width: 6px;
  height: 85%;
  border-top-right-radius: 6px;
  border-bottom-right-radius: 6px;
}

.summary-card.correct::before {
  background: #198754;
}

.summary-card.incorrect::before {
  background: #dc3545;
}

.summary-card.not-attempted::before {
  background: #6c757d;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.summary-icon {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #f8f9fa;
}

.summary-card.correct .summary-icon {
  background: #e8f5e9;
}

.summary-card.incorrect .summary-icon {
  background: #fce8e8;
}

.summary-card.not-attempted .summary-icon {
  background: #e9ecef;
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.summary-marks {
  font-size: 0.8rem;
  font-weight: 500;
}

.summary-card.correct .summary-marks {
  color: #198754;
}

.summary-card.incorrect .summary-marks {
  color: #dc3545;
}

.summary-card.not-attempted .summary-marks {
  color: #6c757d;
}
</style>