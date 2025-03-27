<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  quiz: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'submit'])
const toast = useToast()
const chapters = ref([])
const loading = ref(false)

const formData = ref({
  name: '',
  description: '',
  chapter_id: '',
  date_of_quiz: '',
  duration: 30
})

// Add function to fetch chapters
const fetchChapters = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get('http://localhost:5000/api/chapters', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    chapters.value = response.data.chapters
  } catch (err) {
    toast.error('Failed to fetch chapters')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Watch for quiz prop changes
watch(() => props.quiz, (newQuiz) => {
  if (newQuiz) {
    formData.value = {
      name: newQuiz.name,
      description: newQuiz.description || '',
      chapter_id: newQuiz.chapter_id,
      date_of_quiz: newQuiz.date_of_quiz ? newQuiz.date_of_quiz.slice(0, 16) : '',
      duration: newQuiz.duration
    }
  }
}, { immediate: true })

// Watch for show prop to fetch chapters when modal opens
watch(() => props.show, (newShow) => {
  if (newShow) {
    fetchChapters()
  }
})

const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    chapter_id: '',
    date_of_quiz: '',
    duration: 30
  }
}

const handleSubmit = () => {
  if (!formData.value.name || !formData.value.date_of_quiz || !formData.value.duration || !formData.value.chapter_id) {
    toast.error('Please fill in all required fields')
    return
  }
  emit('submit', { ...formData.value })
}

const handleClose = () => {
  resetForm()
  emit('close')
}

onMounted(() => {
  if (props.isEdit && props.quiz) {
    // Format the date to be compatible with datetime-local input
    const formattedDate = props.quiz.date_of_quiz ? props.quiz.date_of_quiz.slice(0, 16) : ''
    formData.value = {
      ...props.quiz,
      date_of_quiz: formattedDate
    }
  }
})
</script>

<template>
  <div class="modal" :class="{ 'd-block': show }" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEdit ? 'Edit Quiz' : 'Create Quiz' }}</h5>
          <button type="button" class="btn-close" @click="handleClose"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label class="form-label">Name <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model="formData.name" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea class="form-control" v-model="formData.description" rows="2"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Chapter <span class="text-danger">*</span></label>
              <select class="form-select" v-model="formData.chapter_id" required>
                <option value="">Select a chapter</option>
                <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                  {{ chapter.subject.name }} - {{ chapter.name }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Date & Time <span class="text-danger">*</span></label>
              <input type="datetime-local" class="form-control" v-model="formData.date_of_quiz" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Duration (minutes) <span class="text-danger">*</span></label>
              <input type="number" class="form-control" v-model="formData.duration" required>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="handleClose">Cancel</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">
            {{ isEdit ? 'Update' : 'Create' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop fade show" v-if="show"></div>
</template>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style> 