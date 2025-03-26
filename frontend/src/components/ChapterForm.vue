<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  chapter: {
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
const subjects = ref([])
const loading = ref(false)

const form = ref({
  name: '',
  description: '',
  subject_id: ''
})

const resetForm = () => {
  form.value = {
    name: '',
    description: '',
    subject_id: ''
  }
}

const fetchSubjects = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('adminToken')
    const response = await axios.get('http://localhost:5000/api/subjects', {
      params: {
        page: 1,
        per_page: 100
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    subjects.value = response.data.subjects
  } catch (err) {
    toast.error('Failed to fetch subjects')
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSubmit = () => {
  if (!form.value.name || !form.value.subject_id) {
    toast.error('Please fill in all required fields')
    return
  }
  emit('submit', { ...form.value })
}

const handleClose = () => {
  resetForm()
  emit('close')
}

// Watch for changes in chapter prop
watch(() => props.chapter, (newChapter) => {
  if (props.isEdit && newChapter) {
    form.value = {
      name: newChapter.name,
      description: newChapter.description,
      subject_id: newChapter.subject_id
    }
  }
}, { immediate: true })

onMounted(async () => {
  await fetchSubjects()
  if (props.isEdit && props.chapter) {
    form.value = {
      name: props.chapter.name,
      description: props.chapter.description,
      subject_id: props.chapter.subject_id
    }
  }
})
</script>

<template>
  <div class="modal fade show" :class="{ 'd-block': show }" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEdit ? 'Edit Chapter' : 'Create New Chapter' }}</h5>
          <button type="button" class="btn-close" @click="handleClose"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label class="form-label">Subject <span class="text-danger">*</span></label>
              <select class="form-select" v-model="form.subject_id" required>
                <option value="">Select a subject</option>
                <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                  {{ subject.name }}
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Name <span class="text-danger">*</span></label>
              <input type="text" class="form-control" v-model="form.name" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea class="form-control" v-model="form.description" rows="4"></textarea>
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