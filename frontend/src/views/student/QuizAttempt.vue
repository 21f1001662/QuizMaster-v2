<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const quizId = route.params.id
const attemptId = ref(null)
const currentQuestionIndex = ref(0)
const questions = ref([])
const currentQuestion = ref(null)
const loading = ref(true)
const timeLeft = ref(0)
const timer = ref(null)
const quizDetails = ref(null)

// State for answers
const selectedOption = ref(null)
const numericAnswer = ref('')

// Add new ref for confirmation dialog
const showConfirmDialog = ref(false)

// Add new refs for success popup
const showSuccessPopup = ref(false)
const quizScore = ref(0)

// Add new ref for show more state
const showFullInstructions = ref(false)

// Add method to get truncated text
const getTruncatedInstructions = (text) => {
  if (!text) return ''
  const words = text.split(' ')
  if (words.length <= 5) return text
  return showFullInstructions.value ? text : words.slice(0, 5).join(' ') + '...'
}

// Fetch quiz details and start attempt
const startQuiz = async () => {
  try {
    const token = localStorage.getItem('studentToken')
    const response = await axios.post(`http://localhost:5000/api/quizzes/${quizId}/start`, {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    if (response.data.error) {
      toast.error(response.data.error)
      router.push('/student/dashboard/quizzes')
      return
    }

    attemptId.value = response.data.id
    questions.value = response.data.responses
    quizDetails.value = response.data
    await fetchQuestion(0)
    
    // Calculate elapsed time and remaining duration
    const startedAt = new Date(response.data.quiz.date_of_quiz).getTime()
    const now = new Date().getTime()
    const elapsedSeconds = Math.floor((now - startedAt) / 1000)
    const totalDurationSeconds = response.data.quiz.duration * 60
    
    // Set remaining time, ensuring it doesn't go negative
    timeLeft.value = Math.max(0, totalDurationSeconds - elapsedSeconds)
    
    // If time already expired, auto-submit
    if (timeLeft.value === 0) {
      await submitQuiz()
      toast.warning('Quiz duration has expired!')
      return
    }
    
    startTimer()
  } catch (err) {
    if (err.response?.data?.error) {
      toast.error(err.response.data.error)
    } else {
      toast.error('Failed to start quiz')
    }
    console.error(err)
    router.push('/student/dashboard/quizzes')
  } finally {
    loading.value = false
  }
}

// Timer functionality
const startTimer = () => {
  timer.value = setInterval(async () => {
    if (timeLeft.value > 0) {
      timeLeft.value--
    } else {
      clearInterval(timer.value)
      await submitQuiz()
      toast.warning('Time is up! Quiz submitted automatically.')
    }
  }, 1000)
}

// Format time function
const formatTime = computed(() => {
  const totalSeconds = timeLeft.value
  const days = Math.floor(totalSeconds / (24 * 60 * 60))
  const hours = Math.floor((totalSeconds % (24 * 60 * 60)) / (60 * 60))
  const minutes = Math.floor((totalSeconds % (60 * 60)) / 60)
  const seconds = totalSeconds % 60

  if (days > 0) {
    return `${days}d ${hours.toString().padStart(2, '0')}h ${minutes.toString().padStart(2, '0')}m ${seconds.toString().padStart(2, '0')}s`
  } else if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}h ${minutes.toString().padStart(2, '0')}m ${seconds.toString().padStart(2, '0')}s`
  } else {
    return `${minutes.toString().padStart(2, '0')}m ${seconds.toString().padStart(2, '0')}s`
  }
})

// Fetch question details
const fetchQuestion = async (index) => {
  try {
    const token = localStorage.getItem('studentToken')
    const questionId = questions.value[index].question_id
    const response = await axios.get(`http://localhost:5000/api/student/questions/${questionId}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    currentQuestion.value = response.data
    currentQuestionIndex.value = index
    
    // Reset answer state
    selectedOption.value = null
    numericAnswer.value = ''
    
    // Set existing answer if any
    if (questions.value[index].is_attempted) {
      if (response.data.type === 'mcq') {
        selectedOption.value = questions.value[index].mcq_question_answer
      } else {
        numericAnswer.value = questions.value[index].numeric_question_answer
      }
    }
  } catch (err) {
    toast.error('Failed to fetch question')
    console.error(err)
  }
}

// Handle answer submission
const submitAnswer = async () => {
  try {
    const token = localStorage.getItem('studentToken')
    const questionId = currentQuestion.value.id
    
    if (currentQuestion.value.type === 'mcq' && !selectedOption.value) {
      toast.warning('Please select an option')
      return
    }
    
    if (currentQuestion.value.type === 'numeric' && !numericAnswer.value) {
      toast.warning('Please enter an answer')
      return
    }

    const payload = currentQuestion.value.type === 'mcq' 
      ? { option_id: selectedOption.value }
      : { answer: parseFloat(numericAnswer.value) }

    await axios.post(
      `http://localhost:5000/api/attempts/${attemptId.value}/questions/${questionId}/respond`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    // Update local state
    questions.value[currentQuestionIndex.value].is_attempted = true
    if (currentQuestion.value.type === 'mcq') {
      questions.value[currentQuestionIndex.value].mcq_question_answer = selectedOption.value
    } else {
      questions.value[currentQuestionIndex.value].numeric_question_answer = numericAnswer.value
    }

    toast.success('Answer saved')
  } catch (err) {
    toast.error('Failed to save answer')
    console.error(err)
  }
}

// Navigation
const goToQuestion = async (index) => {
  if (index === currentQuestionIndex.value) return
  await fetchQuestion(index)
}

const nextQuestion = async () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    // Save current answer before navigating
    await submitAnswer()
    await goToQuestion(currentQuestionIndex.value + 1)
  } else {
    showConfirmDialog.value = true
  }
}

const previousQuestion = async () => {
  if (currentQuestionIndex.value > 0) {
    // Save current answer before navigating
    await submitAnswer()
    await goToQuestion(currentQuestionIndex.value - 1)
  }
}

// Submit quiz
const submitQuiz = async () => {
  try {
    const token = localStorage.getItem('studentToken')
    const response = await axios.post(
      `http://localhost:5000/api/attempts/${attemptId.value}/submit`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    clearInterval(timer.value)
    quizScore.value = response.data.score
    showSuccessPopup.value = true
  } catch (err) {
    toast.error('Failed to submit quiz')
    console.error(err)
  }
}

// Add new function for final submit
const handleFinalSubmit = async () => {
  showConfirmDialog.value = false
  await submitAnswer()
  await submitQuiz()
}

// Add new function for home navigation
const goToHome = () => {
  router.push('/student/dashboard/quizzes')
}

onMounted(() => {
  startQuiz()
})

// Cleanup
onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<template>
  <div class="container py-4">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="quiz-container">
      <!-- Header -->
      <div class="quiz-header mb-4">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h2 class="mb-1" style="font-size: 1.5rem;">{{ quizDetails?.quiz?.name }}</h2>
            <div class="text-muted mb-0">
              <p class="d-inline" style="font-size: 0.8rem;">{{ getTruncatedInstructions(quizDetails?.quiz?.instructions) }}</p>
              <button 
                v-if="quizDetails?.quiz?.instructions && quizDetails.quiz.instructions.split(' ').length > 5"
                class="btn btn-link btn-sm text-primary p-0 ms-1"
                style="font-size: 0.8rem;"
                @click="showFullInstructions = !showFullInstructions"
              >
                {{ showFullInstructions ? 'Show Less' : 'Show More' }}
              </button>
            </div>
          </div>
          <div class="col-md-6 text-md-end">
            <div class="timer-badge">
              <i class="bi bi-clock me-2"></i>
              {{ formatTime }}
            </div>
            <button class="btn btn-danger ms-3" @click="submitQuiz">
              <i class="bi bi-check-circle me-2"></i>Submit Quiz
            </button>
          </div>
        </div>
      </div>

      <!-- Question Navigation -->
      <div class="question-nav mb-4">
        <div class="d-flex gap-2 flex-wrap">
          <button
            v-for="(question, index) in questions"
            :key="question.id"
            class="question-nav-btn"
            :class="{
              'active': index === currentQuestionIndex,
              'answered': question.is_attempted,
              'current': index === currentQuestionIndex
            }"
            @click="goToQuestion(index)"
          >
            {{ index + 1 }}
          </button>
        </div>
      </div>

      <!-- Question Content -->
      <div class="question-content">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title mb-4">
              Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
            </h5>

            <div class="question-text mb-4">
              {{ currentQuestion?.mcq_question?.question_text || currentQuestion?.numeric_question?.question_text }}
            </div>

            <!-- MCQ Options -->
            <div v-if="currentQuestion?.type === 'mcq'" class="options-list">
              <div
                v-for="(option, index) in currentQuestion.mcq_question.options"
                :key="option.id"
                class="option-item"
                :class="{ 'selected': selectedOption === option.id }"
                @click="selectedOption = option.id"
              >
                <div class="option-circle">
                  {{ String.fromCharCode(65 + index) }}
                </div>
                <div class="option-text">{{ option.text }}</div>
              </div>
            </div>

            <!-- Numeric Input -->
            <div v-else class="numeric-input">
              <input
                type="number"
                class="form-control form-control-lg"
                v-model="numericAnswer"
                placeholder="Enter your answer"
                step="any"
              >
            </div>

            <!-- Navigation Buttons -->
            <div class="d-flex justify-content-between mt-4">
              <button
                class="btn btn-outline-primary"
                :disabled="currentQuestionIndex === 0"
                @click="previousQuestion"
              >
                <i class="bi bi-arrow-left me-2"></i>Previous
              </button>
              
              <button
                class="btn btn-primary"
                :disabled="currentQuestionIndex === questions.length - 1 && currentQuestionIndex !== questions.length - 1"
                @click="nextQuestion"
              >
                {{ currentQuestionIndex === questions.length - 1 ? 'Final Submit' : 'Submit and Next' }}
                <i class="bi bi-arrow-right ms-2"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirmation Dialog -->
  <div v-if="showConfirmDialog" class="modal-backdrop show" style="display: block;"></div>
  <div v-if="showConfirmDialog" class="modal show" style="display: block;">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Confirm Submission</h5>
          <button type="button" class="btn-close" @click="showConfirmDialog = false"></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to submit the quiz? This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showConfirmDialog = false">Cancel</button>
          <button type="button" class="btn btn-primary" @click="handleFinalSubmit">Submit Quiz</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Success Popup -->
  <div v-if="showSuccessPopup" class="modal-backdrop show" style="display: block;"></div>
  <div v-if="showSuccessPopup" class="modal show" style="display: block;">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content success-modal">
        <div class="modal-body text-center p-5">
          <div class="success-emoji mb-4">🎉</div>
          <h4 class="mb-3">Congratulations!</h4>
          <p class="text-muted mb-4">You have successfully attempted the quiz.</p>
          <div class="score-display">
            <div class="score-label">Your Score</div>
            <div class="score-value">{{ quizScore }}</div>
          </div>
          <div class="mt-4">
            <button class="btn btn-primary btn-lg home-button" @click="goToHome">
              <i class="bi bi-house-door me-2"></i>Back to Quizzes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.quiz-container {
  max-width: 1000px;
  margin: 0 auto;
}

.quiz-header {
  background: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.timer-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  font-weight: 500;
  color: #dc3545;
}

.question-nav {
  background: #fff;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.question-nav-btn {
  width: 40px;
  height: 40px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  background: #fff;
  color: #6c757d;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.question-nav-btn:hover {
  border-color: #0d6efd;
  color: #0d6efd;
}

.question-nav-btn.active {
  background: #0d6efd;
  border-color: #0d6efd;
  color: #fff;
}

.question-nav-btn.answered {
  background: #198754;
  border-color: #198754;
  color: #fff;
}

.question-content {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card {
  border: none;
  border-radius: 12px;
}

.question-text {
  font-size: 1.1rem;
  color: #2c3e50;
  line-height: 1.6;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-item:hover {
  border-color: #0d6efd;
  background: #f8f9fa;
}

.option-item.selected {
  border-color: #0d6efd;
  background: #e7f1ff;
}

.option-circle {
  width: 32px;
  height: 32px;
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

.option-text {
  font-size: 1rem;
}

.numeric-input .form-control {
  font-size: 1.1rem;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid #e9ecef;
}

.numeric-input .form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

.btn {
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
}

.btn-primary {
  background: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary:hover {
  background: #0b5ed7;
  border-color: #0a58ca;
}

.btn-outline-primary {
  color: #0d6efd;
  border-color: #0d6efd;
}

.btn-outline-primary:hover {
  background: #0d6efd;
  border-color: #0d6efd;
}

.btn-danger {
  background: #dc3545;
  border-color: #dc3545;
}

.btn-danger:hover {
  background: #bb2d3b;
  border-color: #b02a37;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 1055;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-dialog {
  margin: 0 auto;
  max-width: 500px;
  width: 100%;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  border-bottom: 1px solid #dee2e6;
  padding: 1rem 1.5rem;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  border-top: 1px solid #dee2e6;
  padding: 1rem 1.5rem;
}

.success-modal {
  border: none;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}

.success-emoji {
  font-size: 4rem;
  line-height: 1;
  animation: bounce 1s infinite;
}

.score-display {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 0 auto;
  max-width: 200px;
}

.score-label {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.score-value {
  font-size: 2.5rem;
  font-weight: 600;
  color: #198754;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Update button styles */
.btn-primary:disabled {
  background-color: #0d6efd;
  border-color: #0d6efd;
  opacity: 0.8;
  cursor: pointer;
}

.home-button {
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
  background: rgba(13, 110, 253, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(13, 110, 253, 0.2);
  transition: all 0.3s ease;
  color: white;
}

.home-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(13, 110, 253, 0.3);
  background: rgba(13, 110, 253, 1);
  border-color: rgba(255, 255, 255, 0.3);
}

.home-button:active {
  transform: translateY(0);
  background: rgba(13, 110, 253, 0.95);
}
</style> 