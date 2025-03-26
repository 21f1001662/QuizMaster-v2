<script setup>
import { ref, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  subject: {
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
  description: ''
})

const resetForm = () => {
  form.value = {
    name: '',
    description: ''
  }
}

const handleSubmit = () => {
  if (!form.value.name) {
    toast.error('Please fill in the subject name')
    return
  }
  emit('submit', { ...form.value })
}

const handleClose = () => {
  resetForm()
  emit('close')
}

// Watch for changes in subject prop
watch(() => props.subject, (newSubject) => {
  if (props.isEdit && newSubject) {
    form.value = { ...newSubject }
  }
}, { immediate: true })

onMounted(() => {
  if (props.isEdit && props.subject) {
    form.value = { ...props.subject }
  }
})
</script>

<template>
  <div class="modal fade show" :class="{ 'd-block': show }" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEdit ? 'Edit Subject' : 'Create New Subject' }}</h5>
          <button type="button" class="btn-close" @click="handleClose"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
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