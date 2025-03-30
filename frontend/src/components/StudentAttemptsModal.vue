<script setup>
import { ref, watch, computed } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'

const props = defineProps({
  show: Boolean,
  userId: Number,
  studentName: String
})

const emit = defineEmits(['close'])

const toast = useToast()
const loading = ref(false)
const attempts = ref([])
const showResponsesModal = ref(false)
const selectedAttempt = ref(null)
const attemptResponses = ref(null)
const loadingResponses = ref(false)

// Add computed properties for response summary
const scoreColor = computed(() => {
  if (!attemptResponses.value) return '#6c757d'
  const percentage = (attemptResponses.value.score / attemptResponses.value.quiz.total_score) * 100
  if (percentage >= 70) return '#198754'
  if (percentage >= 35) return '#f9c924'
  return '#dc3545'
})

watch(() => props.show, async (newVal) => {
  if (newVal && props.userId) {
    await fetchAttempts()
  }
})

const fetchAttempts = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get(`http://localhost:5000/api/attempts`, {
      params: {
        user_id: props.userId,
        page: 1,
        per_page: 10,
        sort_by: 'created_at',
        sort_order: 'desc'
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    attempts.value = response.data.attempts
  } catch (error) {
    toast.error('Failed to fetch attempts')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchAttemptResponses = async (attemptId) => {
  try {
    loadingResponses.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get(`http://localhost:5000/api/attempts/${attemptId}/responses`, {
      params: {
        user_id: props.userId
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    attemptResponses.value = response.data
    showResponsesModal.value = true
  } catch (error) {
    toast.error('Failed to fetch responses')
    console.error(error)
  } finally {
    loadingResponses.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDuration = (minutes) => {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
}

const getOptionLetter = (index) => {
  return String.fromCharCode(65 + index)
}

const formatNumericAnswer = (value) => {
  return Number(value).toFixed(2)
}

const closeModal = () => {
  emit('close')
  attempts.value = []
  showResponsesModal.value = false
  selectedAttempt.value = null
  attemptResponses.value = null
}
</script>

<template>
  <div v-if="show" class="modal-backdrop fade show"></div>
  
  <div v-if="show" class="modal fade show d-block" tabindex="-1">
    <div class="modal-dialog modal-xl modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            {{ studentName }}'s Attempts
          </h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        
        <div class="modal-body">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else-if="attempts.length === 0" class="text-center py-4">
            <p class="text-muted">No attempts found</p>
          </div>
          
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Quiz Name</th>
                  <th>Subject</th>
                  <th>Chapter</th>
                  <th>Date Attempted</th>
                  <th>Score</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="attempt in attempts" :key="attempt.id">
                  <td>{{ attempt.quiz.name }}</td>
                  <td>{{ attempt.quiz.chapter.subject.name }}</td>
                  <td>{{ attempt.quiz.chapter.name }}</td>
                  <td>{{ formatDate(attempt.created_at) }}</td>
                  <td>
                    <span 
                      class="badge"
                      :class="{
                        'bg-success': attempt.score >= 0.7 * attempt.quiz.total_score,
                        'bg-warning': attempt.score >= 0.35 * attempt.quiz.total_score && attempt.score < 0.7 * attempt.quiz.total_score,
                        'bg-danger': attempt.score < 0.35 * attempt.quiz.total_score
                      }"
                    >
                      {{ attempt.score }}/{{ attempt.quiz.total_score }}
                      ({{ ((attempt.score / attempt.quiz.total_score) * 100).toFixed(1) }}%)
                    </span>
                  </td>
                  <td>
                    <button 
                      class="btn btn-sm btn-primary"
                      @click="fetchAttemptResponses(attempt.id)"
                      :disabled="loadingResponses"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View Responses
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Responses Modal -->
  <div v-if="showResponsesModal" class="modal-backdrop show" style="display: block;"></div>
  <div v-if="showResponsesModal" class="modal show" style="display: block;">
    <div class="modal-dialog modal-dialog-centered modal-xl">
      <div class="modal-content responses-modal">
        <div class="modal-header border-0">
          <h5 class="modal-title">Quiz Responses</h5>
          <button type="button" class="btn-close" @click="showResponsesModal = false"></button>
        </div>
        
        <div class="modal-body">
          <!-- Loading State -->
          <div v-if="loadingResponses" class="text-center py-5">
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
                    {{ attemptResponses?.score }} / {{ attemptResponses?.quiz.total_score }}
                  </div>
                </div>
                <div class="text-end">
                  <h6 class="mb-1">Completion Date</h6>
                  <div class="text-muted">{{ formatDate(attemptResponses?.completed_at) }}</div>
                </div>
              </div>
            </div>

            <!-- Questions List -->
            <div class="questions-list">
              <div v-for="(response, index) in attemptResponses?.responses" :key="response.id" class="question-card mb-4">
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
          <button type="button" class="btn btn-secondary" @click="showResponsesModal = false">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.badge {
  font-weight: 500;
  padding: 0.5em 0.8em;
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
}

.response-summary {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 12px;
}

.question-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.question-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
  margin-bottom: 1rem;
}

.question-status.correct {
  background: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.question-status.incorrect {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.question-status.not-attempted {
  background: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.question-number {
  font-weight: 600;
  color: #2c3e50;
}

.question-marks {
  font-weight: 500;
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
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  transition: all 0.2s ease;
}

.option-item.selected {
  background: #e9ecef;
}

.option-item.correct {
  background: rgba(25, 135, 84, 0.1);
  border-color: #198754;
}

.option-item.incorrect {
  background: rgba(220, 53, 69, 0.1);
  border-color: #dc3545;
}

.option-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  color: #6c757d;
}

.option-text {
  flex: 1;
}

.option-status i {
  font-size: 1.2rem;
}

.numeric-answer {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
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
  color: #2c3e50;
}

.modal-xl {
  max-width: 60%;
  margin: 1.75rem auto;
}

.table {
  min-width: 1000px; /* Ensure table has a minimum width */
}

.table th, .table td {
  white-space: nowrap;
  padding: 1rem;
}

.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Make sure the modal doesn't get too close to the screen edges on mobile */
@media (max-width: 768px) {
  .modal-xl {
    max-width: 98%;
    margin: 0.5rem auto;
  }
}
</style> 