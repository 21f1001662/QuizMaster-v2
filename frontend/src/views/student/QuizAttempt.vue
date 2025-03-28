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
    
    // Start timer (assuming 60 minutes duration)
    timeLeft.value = 60 * 60 // in seconds
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
  timer.value = setInterval(() => {
    if (timeLeft.value > 0) {
      timeLeft.value--
    } else {
      submitQuiz()
    }
  }, 1000)
}

const formatTime = computed(() => {
  const minutes = Math.floor(timeLeft.value / 60)
  const seconds = timeLeft.value % 60
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
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
  
  // Save current answer before navigating
  if (questions.value[currentQuestionIndex.value].is_attempted) {
    await submitAnswer()
  }
  
  await fetchQuestion(index)
}

const nextQuestion = async () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    await goToQuestion(currentQuestionIndex.value + 1)
  }
}

const previousQuestion = async () => {
  if (currentQuestionIndex.value > 0) {
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
    
    // Show success modal with score
    toast.success(`Quiz completed! Your score: ${response.data.score}`)
    
    // Redirect after a short delay
    setTimeout(() => {
      router.push('/student/dashboard/quizzes')
    }, 2000)
  } catch (err) {
    toast.error('Failed to submit quiz')
    console.error(err)
  }
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
            <h2 class="mb-1">{{ quizDetails?.quiz?.name }}</h2>
            <p class="text-muted mb-0">{{ quizDetails?.quiz?.instructions }}</p>
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
                @click="nextQuestion"
                :disabled="currentQuestionIndex === questions.length - 1"
              >
                Next<i class="bi bi-arrow-right ms-2"></i>
              </button>
            </div>
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
</style> 