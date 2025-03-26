<script setup>
defineProps({
  columns: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    required: true
  },
  searchPlaceholder: {
    type: String,
    default: 'Search...'
  },
  createButtonText: {
    type: String,
    default: 'Create New'
  },
  modelValue: {
    type: String,
    default: ''
  }
})

defineEmits(['search', 'create', 'edit', 'delete', 'update:modelValue'])
</script>

<template>
  <div class="card">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div class="input-group" style="max-width: 300px;">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control" 
            :placeholder="searchPlaceholder" 
            :value="modelValue"
            @input="$emit('update:modelValue', $event.target.value); $emit('search', $event.target.value)"
          >
        </div>
        <button class="btn btn-primary" @click="$emit('create')">
          <i class="bi bi-plus-lg me-2"></i>{{ createButtonText }}
        </button>
      </div>

      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in data" :key="item.id">
              <td v-for="column in columns" :key="column.key">
                {{ item[column.key] }}
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-2" @click="$emit('edit', item)">
                  <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="$emit('delete', item)">
                  <i class="bi bi-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}
</style> 