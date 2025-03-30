<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useToast } from 'vue-toastification'
import { Modal } from 'bootstrap'
import QuizForm from '../../components/QuizForm.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

const quiz = ref(null)
const questions = ref([])
const loading = ref(false)
const error = ref(null)
const questionModal = ref(null)
const aiModal = ref(null)
const selectedQuestion = ref(null)
const isEditMode = ref(false)
const questionType = ref('mcq')
const showQuizModal = ref(false)
const showAIModal = ref(false)
const formData = ref({
  type: 'mcq',
  question_text: '',
  correct_marks: 4,
  incorrect_marks: 0,
  options: [],
  answer_lower_bound: 0,
  answer_upper_bound: 0
})

const aiFormData = ref({
  context: '',
  question_type: 'mcq',
  num_questions: 5,
  correct_marks: 4,
  incorrect_marks: -1
})

const isGenerating = ref(false)
const generatedQuestions = ref([])

const fetchQuiz = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get(`http://localhost:5000/api/quizzes`, {
      params: {
        quiz_id: route.params.id
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    quiz.value = response.data.quizzes[0]
    questions.value = quiz.value.questions
  } catch (err) {
    error.value = 'Failed to fetch quiz'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleCreateQuestion = () => {
  isEditMode.value = false
  selectedQuestion.value = null
  questionType.value = 'mcq'
  formData.value = {
    type: 'mcq',
    question_text: '',
    correct_marks: 4,
    incorrect_marks: 0,
    options: [],
    answer_lower_bound: 0,
    answer_upper_bound: 0
  }
  questionModal.value.show()
}

const handleEditQuestion = (question) => {
  isEditMode.value = true
  selectedQuestion.value = question
  questionType.value = question.type
  formData.value = {
    type: question.type,
    question_text: question.question_details.question_text,
    correct_marks: question.question_details.correct_marks,
    incorrect_marks: question.question_details.incorrect_marks,
    options: question.question_details.options || [],
    answer_lower_bound: question.question_details.answer_lower_bound || 0,
    answer_upper_bound: question.question_details.answer_upper_bound || 0
  }
  questionModal.value.show()
}

const handleDeleteQuestion = async (question) => {
  if (!confirm('Are you sure you want to delete this question?')) return

  try {
    const token = localStorage.getItem('adminToken')
    await axios.delete(`http://localhost:5000/api/quizzes/${route.params.id}/questions/${question.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    toast.success('Question deleted successfully')
    fetchQuiz()
  } catch (err) {
    toast.error('Failed to delete question')
    console.error(err)
  }
}

const handleCloseModal = () => {
  questionModal.value.hide()
}

const handleSubmitQuestion = async () => {
  if (!validateForm()) return

  try {
    const token = localStorage.getItem('adminToken')
    if (isEditMode.value) {
      await axios.put(`http://localhost:5000/api/quizzes/${route.params.id}/questions/${selectedQuestion.value.id}`, formData.value, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      toast.success('Question updated successfully')
    } else {
      await axios.post(`http://localhost:5000/api/quizzes/${route.params.id}/questions`, formData.value, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      toast.success('Question created successfully')
    }
    questionModal.value.hide()
    fetchQuiz()
  } catch (err) {
    toast.error(isEditMode.value ? 'Failed to update question' : 'Failed to create question')
    console.error(err)
  }
}

const addOption = () => {
  formData.value.options.push({
    text: '',
    is_correct: false
  })
}

const removeOption = (index) => {
  formData.value.options.splice(index, 1)
}

const handleCorrectOptionChange = (changedIndex) => {
  // If the changed option is being marked as correct, unmark all other options
  if (formData.value.options[changedIndex].is_correct) {
    formData.value.options.forEach((option, index) => {
      if (index !== changedIndex) {
        option.is_correct = false
      }
    })
  }
}

const validateForm = () => {
  if (!formData.value.question_text) {
    toast.error('Question text is required')
    return false
  }
  if (formData.value.type === 'mcq') {
    if (formData.value.options.length < 2) {
      toast.error('At least two options are required')
      return false
    }
    const correctOptions = formData.value.options.filter(opt => opt.is_correct)
    if (correctOptions.length !== 1) {
      toast.error('Exactly one option must be marked as correct')
      return false
    }
  } else {
    if (!formData.value.answer_lower_bound || !formData.value.answer_upper_bound) {
      toast.error('Answer bounds are required')
      return false
    }
  }
  return true
}

const handleEditQuiz = () => {
  showQuizModal.value = true
}

const handleDeleteQuiz = async () => {
  if (!confirm('Are you sure you want to delete this quiz?')) return

  try {
    const token = localStorage.getItem('adminToken')
    await axios.delete(`http://localhost:5000/api/quizzes/${quiz.value.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    toast.success('Quiz deleted successfully')
    router.push('/admin/dashboard/quizzes')
  } catch (err) {
    toast.error('Failed to delete quiz')
    console.error(err)
  }
}

const handleQuizUpdate = async (formData) => {
  try {
    const token = localStorage.getItem('adminToken')
    await axios.put(`http://localhost:5000/api/quizzes/${quiz.value.id}`, formData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    toast.success('Quiz updated successfully')
    showQuizModal.value = false
    fetchQuiz()
  } catch (err) {
    toast.error('Failed to update quiz')
    console.error(err)
  }
}

const handleAddQuestion = () => {
  handleCreateQuestion()
}

const handleCloseAIModal = () => {
  aiModal.value.hide()
  aiFormData.value = {
    context: '',
    question_type: 'mcq',
    num_questions: 5,
    correct_marks: 4,
    incorrect_marks: -1
  }
}

const handleGenerateQuestions = async () => {
  if (!aiFormData.value.context) {
    toast.error('Context is required')
    return
  }

  try {
    isGenerating.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.post(`http://localhost:5000/api/quizzes/${route.params.id}/ai/generate`, aiFormData.value, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    generatedQuestions.value = response.data.questions
    toast.success(response.data.message)
    aiModal.value.hide()
    fetchQuiz()
  } catch (err) {
    toast.error('Failed to generate questions')
    console.error(err)
  } finally {
    isGenerating.value = false
  }
}

onMounted(() => {
  fetchQuiz()
  questionModal.value = new Modal(document.getElementById('questionModal'))
  aiModal.value = new Modal(document.getElementById('aiModal'))
})
</script>

<template>
  <div class="quiz-build-page">
    <!-- Header Section -->
    <div class="header-section mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
          <button class="btn btn-link text-dark me-3 p-0" @click="router.push('/admin/dashboard/quizzes')">
            <i class="bi bi-arrow-left fs-4"></i>
          </button>
          <div>
            <div class="d-flex align-items-center mb-1">
              <h2 class="mb-0">{{ quiz?.name }}</h2>
            </div>
            <div class="d-flex align-items-center text-muted">
              <div class="me-3">
                <i class="bi bi-book me-1"></i>
                {{ quiz?.chapter?.subject?.name }}
              </div>
              <div class="me-3">
                <i class="bi bi-journal-text me-1"></i>
                {{ quiz?.chapter?.name }}
              </div>
              <div>
                <i class="bi bi-clock me-1"></i>
                {{ quiz?.duration }} minutes
              </div>
            </div>
          </div>
        </div>
        <div class="d-flex align-items-center gap-3">
          <button class="btn btn-icon" @click="handleEditQuiz" title="Edit Quiz">
            <i class="bi bi-pencil text-primary"></i>
          </button>
          <button class="btn btn-icon" @click="handleDeleteQuiz" title="Delete Quiz">
            <i class="bi bi-trash text-danger"></i>
          </button>
          <button v-if="questions.length !== 0" class="btn btn-gradient" @click="aiModal.show()">
            <i class="bi bi-robot me-2"></i>Generate with AI
          </button>
          <button class="btn btn-primary" @click="handleAddQuestion">
            <i class="bi bi-plus-lg me-2"></i>Add Question
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Questions List -->
    <div v-else>
      <div v-if="questions.length === 0" class="empty-state">
        <div class="text-center py-5">
          <i class="bi bi-journal-text display-1 text-muted mb-3"></i>
          <h4>No Questions Yet</h4>
          <p class="text-muted">Start building your quiz by adding questions</p>
          <button class="mt-2 btn btn-gradient" @click="aiModal.show()">
            <i class="bi bi-robot me-2"></i>Generate Questions with AI
          </button>
        </div>
      </div>

      <div v-else class="questions-grid">
        <div v-for="(question, index) in questions" 
             :key="question.id" 
             class="question-card">
          <div class="question-header">
            <div class="d-flex align-items-center">
              <span class="question-number">{{ index + 1 }}</span>
              <span class="question-text">{{ question.question_details.question_text }}</span> 
            </div>
            <div class="question-actions">
              <button class="btn btn-icon" @click="handleEditQuestion(question)" title="Edit Question">
                <i class="bi bi-pencil text-primary"></i>
              </button>
              <button class="btn btn-icon" @click="handleDeleteQuestion(question)" title="Delete Question">
                <i class="bi bi-trash text-danger"></i>
              </button>
            </div>
          </div>

          <div class="question-content">
            
            
            
            <div class="question-marks">
              <span class="question-type" :class="question.type">
                {{ question.type.toUpperCase() }}
              </span>
              <span class="mark correct">
                <i class="bi bi-check-circle-fill"></i>
                +{{ question.question_details.correct_marks }}
              </span>
              <span class="mark incorrect">
                <i class="bi bi-x-circle-fill"></i>
                {{ question.question_details.incorrect_marks }}
              </span>
            </div>

            <!-- MCQ Options -->
            <div v-if="question.type === 'mcq'" class="options-list">
              <div v-for="(option, optIndex) in question.question_details.options" 
                   :key="optIndex"
                   class="option-item"
                   :class="{ 'correct': option.is_correct }">
                <div class="option-circle">{{ String.fromCharCode(65 + optIndex) }}</div>
                <div class="option-text">{{ option.text }}</div>
                <div class="option-status">
                  <i v-if="option.is_correct" class="bi bi-check-circle-fill text-success"></i>
                </div>
              </div>
            </div>

            <!-- Numeric Answer Range -->
            <div v-else class="numeric-range">
              <div class="range-label">Answer Range</div>
              <div class="range-values">
                <span class="range-value">{{ question.question_details.answer_lower_bound }}</span>
                <i class="bi bi-arrow-left-right mx-2"></i>
                <span class="range-value">{{ question.question_details.answer_upper_bound }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Question Modal -->
    <div class="modal fade" id="questionModal" tabindex="-1" aria-labelledby="questionModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header border-0">
            <h5 class="modal-title" id="questionModalLabel">{{ isEditMode ? 'Edit Question' : 'Add Question' }}</h5>
            <button type="button" class="btn-close" @click="handleCloseModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-4">
              <label class="form-label">Question Type</label>
              <select class="form-select" v-model="questionType" @change="formData.type = questionType">
                <option value="mcq">Multiple Choice</option>
                <option value="numeric">Numeric</option>
              </select>
            </div>

            <div class="mb-4">
              <label class="form-label">Question Text</label>
              <textarea class="form-control" v-model="formData.question_text" rows="3"></textarea>
            </div>

            <div class="row mb-4">
              <div class="col-md-6">
                <label class="form-label">Correct Marks</label>
                <input type="number" class="form-control" v-model="formData.correct_marks" min="0" step="0.5">
              </div>
              <div class="col-md-6">
                <label class="form-label">Incorrect Marks</label>
                <input type="number" class="form-control" v-model="formData.incorrect_marks" max="0" step="0.5">
              </div>
            </div>

            <template v-if="questionType === 'mcq'">
              <div class="mb-4">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <label class="form-label mb-0">Options</label>
                  <button type="button" class="btn btn-outline-primary btn-sm" @click="addOption">
                    <i class="bi bi-plus-lg"></i> Add Option
                  </button>
                </div>
                <div v-for="(option, index) in formData.options" :key="index" class="option-input-group mb-2">
                  <div class="input-group">
                    <span class="input-group-text option-circle-edit">{{ String.fromCharCode(65 + index) }}</span>
                    <input type="text" class="form-control" v-model="option.text" placeholder="Option text">
                    <div class="input-group-text">
                      <div class="form-check">
                        <input type="checkbox" class="form-check-input" 
                               v-model="option.is_correct"
                               @change="handleCorrectOptionChange(index)">
                        <label class="form-check-label">Correct</label>
                      </div>
                    </div>
                    <button class="btn btn-outline-danger" type="button" @click="removeOption(index)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </template>

            <template v-else>
              <div class="row mb-4">
                <div class="col-md-6">
                  <label class="form-label">Lower Bound</label>
                  <input type="number" class="form-control" v-model="formData.answer_lower_bound" step="any">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Upper Bound</label>
                  <input type="number" class="form-control" v-model="formData.answer_upper_bound" step="any">
                </div>
              </div>
            </template>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" @click="handleCloseModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="handleSubmitQuestion">
              {{ isEditMode ? 'Update' : 'Create' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Form Modal -->
    <QuizForm
      :show="showQuizModal"
      :quiz="quiz"
      :is-edit="true"
      @close="showQuizModal = false"
      @submit="handleQuizUpdate"
    />

    <!-- AI Generation Modal -->
    <div class="modal fade" id="aiModal" tabindex="-1" aria-labelledby="aiModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header border-0">
            <h5 class="modal-title" id="aiModalLabel">Generate Questions with AI</h5>
            <button type="button" class="btn-close" @click="handleCloseAIModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-4">
              <label class="form-label">Context</label>
              <textarea 
                class="form-control" 
                v-model="aiFormData.context" 
                rows="4" 
                placeholder="Enter the context for question generation (e.g., 'gravitation related questions, easy')"
              ></textarea>
            </div>

            <div class="row mb-4">
              <div class="col-md-6">
                <label class="form-label">Question Type</label>
                <select class="form-select" v-model="aiFormData.question_type">
                  <option value="mcq">Multiple Choice</option>
                  <option value="numeric">Numeric</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Number of Questions</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="aiFormData.num_questions" 
                  min="1" 
                  max="10"
                >
              </div>
            </div>

            <div class="row mb-4">
              <div class="col-md-6">
                <label class="form-label">Correct Marks</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="aiFormData.correct_marks" 
                  min="0" 
                  step="0.5"
                >
              </div>
              <div class="col-md-6">
                <label class="form-label">Incorrect Marks</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="aiFormData.incorrect_marks" 
                  max="0" 
                  step="0.5"
                >
              </div>
            </div>
          </div>
          <div class="modal-footer border-0">
            <button type="button" class="btn btn-light" @click="handleCloseAIModal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="handleGenerateQuestions"
              :disabled="isGenerating"
            >
              <span v-if="isGenerating" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ isGenerating ? 'Generating...' : 'Generate' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.quiz-build-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.btn-icon {
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: rgba(0,0,0,0.05);
}

.btn-gradient {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  color: white;
  background: linear-gradient(135deg, #34d399, #10b981);
}

.empty-state {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.questions-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.question-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.question-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-number {
  background: var(--bs-primary);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.question-text {
  font-size: 1.1rem;
  color: #2c3e50;
  line-height: 1.5;
  margin: 0;
}

.question-type {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.question-type.mcq {
  background: #e3f2fd;
  color: #1976d2;
}

.question-type.numeric {
  background: #e8f5e9;
  color: #2e7d32;
}

.question-marks {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.mark {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.mark.correct {
  background: #e8f5e9;
  color: #2e7d32;
}

.mark.incorrect {
  background: #fce8e8;
  color: #dc3545;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.2s ease;
}

.option-item.correct {
  background: #e8f5e9;
}

.option-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  margin-right: 1rem;
}

.option-circle-edit {
  background: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
}

.option-item.correct .option-circle {
  background: #2e7d32;
  color: white;
}

.option-text {
  flex: 1;
}

.option-status {
  font-size: 1.2rem;
}

.numeric-range {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.range-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.range-values {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.range-value {
  color: #2e7d32;
}

.option-input-group .input-group-text {
  background: #f8f9fa;
  border-right: none;
}

.option-input-group .form-control {
  border-left: none;
}

.option-input-group .input-group-text:last-child {
  border-left: none;
}

.modal-content {
  border: none;
  border-radius: 12px;
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

.form-label {
  font-weight: 500;
  color: #2c3e50;
}

.form-control:focus, .form-select:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

.btn-light {
  background: #f8f9fa;
  border: none;
  color: #2c3e50;
}

.btn-light:hover {
  background: #e9ecef;
}
</style> 