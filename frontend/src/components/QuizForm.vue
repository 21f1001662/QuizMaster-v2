<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  quiz: {
    type: Object,
    default: () => ({})
  },
  isEdit: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'submit'])

const toast = useToast()

const form = ref({
  name: '',
  chapter_id: 1,
  date_of_quiz: '',
  duration: 60,
  total_questions: 0,
  remarks: '',
  instructions: ''
})

const resetForm = () => {
  form.value = {
    name: '',
    chapter_id: 1,
    date_of_quiz: '',
    duration: 60,
    total_questions: 0,
    remarks: '',
    instructions: ''
  }
}

const handleSubmit = () => {
  if (!form.value.name || !form.value.date_of_quiz || !form.value.duration) {
    toast.error('Please fill in all required fields')
    return
  }
  emit('submit', { ...form.value })
}

const handleClose = () => {
  resetForm()
  emit('close')
}

// Watch for changes in quiz prop
watch(() => props.quiz, (newQuiz) => {
  if (props.isEdit && newQuiz) {
    // Format the date to be compatible with datetime-local input
    const formattedDate = newQuiz.date_of_quiz ? newQuiz.date_of_quiz.slice(0, 16) : ''
    form.value = {
      ...newQuiz,
      date_of_quiz: formattedDate
    }
  }
}, { immediate: true })

onMounted(() => {
  if (props.isEdit && props.quiz) {
    // Format the date to be compatible with datetime-local input
    const formattedDate = props.quiz.date_of_quiz ? props.quiz.date_of_quiz.slice(0, 16) : ''
    form.value = {
      ...props.quiz,
      date_of_quiz: formattedDate
    }
  }
})
</script>

<template>
  <div class="modal fade show" :class="{ 'd-block': show }" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEdit ? 'Edit Quiz' : 'Create New Quiz' }}</h5>
          <button type="button" class="btn-close" @click="handleClose"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label class="form-label">Name <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model="form.name" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Chapter ID <span class="text-danger">*</span></label>
              <input type="number" class="form-control" v-model="form.chapter_id" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Date & Time <span class="text-danger">*</span></label>
              <input type="datetime-local" class="form-control" v-model="form.date_of_quiz" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Duration (minutes) <span class="text-danger">*</span></label>
              <input type="number" class="form-control" v-model="form.duration" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Total Questions</label>
              <input type="number" class="form-control" v-model="form.total_questions">
            </div>
            <div class="mb-3">
              <label class="form-label">Remarks</label>
              <textarea class="form-control" v-model="form.remarks" rows="2"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Instructions</label>
              <textarea class="form-control" v-model="form.instructions" rows="3"></textarea>
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
  <div v-if="show" class="modal-backdrop fade show"></div>
</template>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style> 