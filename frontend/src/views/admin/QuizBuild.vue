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
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
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
      <div class="d-flex align-items-center">
        <i class="bi bi-pencil text-primary me-3 cursor-pointer hover-opacity" @click="handleEditQuiz"></i>
        <i class="bi bi-trash text-danger me-3 cursor-pointer hover-opacity" @click="handleDeleteQuiz"></i>
        <button class="btn btn-outline-primary me-2 generate-ai-btn" @click="aiModal.show()">
          <span class="btn-content">
            <i class="bi bi-robot me-2"></i>Generate with AI
          </span>
          <span class="glass-reflection"></span>
        </button>
        <button class="btn btn-primary" @click="handleAddQuestion">
          <i class="bi bi-plus-lg me-2"></i>Add Question
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else class="card">
      <div class="card-body">
        <div v-if="questions.length === 0" class="text-center py-5">
          <p class="text-muted">No questions added yet. Click the button above to add a question.</p>
        </div>

        <div v-else class="list-group">
          <div v-for="(question, index) in questions" :key="question.id" class="list-group-item border-0 mb-4">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <div class="d-flex align-items-center mb-2">
                  <span class="badge bg-primary me-2">Question {{ index + 1 }}</span>
                  <span class="badge" :class="question.type === 'mcq' ? 'bg-info' : 'bg-success'">
                    {{ question.type.toUpperCase() }}
                  </span>
                </div>
                <h5 class="mb-2">{{ question.question_details.question_text }}</h5>
                <div class="text-muted small">
                  <span class="me-3">
                    <i class="bi bi-check-circle-fill text-success me-1"></i>
                    +{{ question.question_details.correct_marks }} marks
                  </span>
                  <span>
                    <i class="bi bi-x-circle-fill text-danger me-1"></i>
                    {{ question.question_details.incorrect_marks }} marks
                  </span>
                </div>
              </div>
              <div>
                <button class="btn btn-sm btn-link text-primary me-2" @click="handleEditQuestion(question)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-link text-danger" @click="handleDeleteQuestion(question)">
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>

            <!-- MCQ Options -->
            <div v-if="question.type === 'mcq'" class="ms-4">
              <div v-for="(option, optIndex) in question.question_details.options" 
                   :key="optIndex"
                   class="d-flex align-items-center mb-2">
                <div class="form-check me-2">
                  <input type="radio" 
                         class="form-check-input" 
                         :checked="option.is_correct"
                         disabled>
                </div>
                <div class="flex-grow-1 p-2 rounded" 
                     :class="option.is_correct ? 'bg-success bg-opacity-10' : 'bg-light'">
                  {{ option.text }}
                </div>
              </div>
            </div>

            <!-- Numeric Answer Range -->
            <div v-else class="ms-4">
              <div class="d-flex align-items-center">
                <i class="bi bi-arrow-left-right me-2"></i>
                <span class="text-muted">
                  Answer should be between 
                  <strong>{{ question.question_details.answer_lower_bound }}</strong> 
                  and 
                  <strong>{{ question.question_details.answer_upper_bound }}</strong>
                </span>
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
          <div class="modal-header">
            <h5 class="modal-title" id="questionModalLabel">{{ isEditMode ? 'Edit Question' : 'Add Question' }}</h5>
            <button type="button" class="btn-close" @click="handleCloseModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Question Type</label>
              <select class="form-select" v-model="questionType" @change="formData.type = questionType">
                <option value="mcq">Multiple Choice</option>
                <option value="numeric">Numeric</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label">Question Text</label>
              <textarea class="form-control" v-model="formData.question_text" rows="3"></textarea>
            </div>

            <div class="row mb-3">
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
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <label class="form-label mb-0">Options</label>
                  <button type="button" class="btn btn-sm btn-outline-primary" @click="addOption">
                    <i class="bi bi-plus-lg"></i> Add Option
                  </button>
                </div>
                <div v-for="(option, index) in formData.options" :key="index" class="input-group mb-2">
                  <input type="text" class="form-control" v-model="option.text" placeholder="Option text">
                  <div class="input-group-text">
                    <input type="checkbox" class="form-check-input mt-0" 
                           v-model="option.is_correct"
                           @change="handleCorrectOptionChange(index)">
                  </div>
                  <button class="btn btn-outline-danger" type="button" @click="removeOption(index)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </template>

            <template v-else>
              <div class="row mb-3">
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
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="handleCloseModal">Cancel</button>
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
          <div class="modal-header">
            <h5 class="modal-title" id="aiModalLabel">Generate Questions with AI</h5>
            <button type="button" class="btn-close" @click="handleCloseAIModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Context</label>
              <textarea 
                class="form-control" 
                v-model="aiFormData.context" 
                rows="4" 
                placeholder="Enter the context for question generation (e.g., 'gravitation related questions, easy')"
              ></textarea>
            </div>

            <div class="row mb-3">
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

            <div class="row mb-3">
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
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="handleCloseAIModal">Cancel</button>
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
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.btn-link {
  text-decoration: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-link:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.btn-link.text-primary:hover {
  color: #0b5ed7 !important;
}

.btn-link.text-danger:hover {
  color: #bb2d3b !important;
}

.list-group-item {
  background-color: #fff;
  border-radius: 8px !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.list-group-item:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.hover-opacity {
  transition: opacity 0.2s ease;
}

.hover-opacity:hover {
  opacity: 0.7;
}

.btn-outline-primary {
  border-width: 2px;
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.spinner-border {
  width: 1rem;
  height: 1rem;
}

.generate-ai-btn {
  position: relative;
  overflow: hidden;
  border-width: 2px;
  background: linear-gradient(135deg, #10b981, #059669, #047857);
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.generate-ai-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  color: white;
  background: linear-gradient(135deg, #34d399, #10b981, #059669);
}

.generate-ai-btn .btn-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.generate-ai-btn .glass-reflection {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.3),
    transparent
  );
  animation: reflection 3s infinite;
  z-index: 2;
}

@keyframes reflection {
  0% {
    left: -100%;
  }
  20% {
    left: 100%;
  }
  100% {
    left: 100%;
  }
}
</style> 