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
  },
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  }
})

defineEmits(['search', 'create', 'edit', 'delete', 'update:modelValue', 'page-change'])

const getCellValue = (item, column) => {
  if (column.formatter) {
    return column.formatter(item)
  }
  return item[column.key]
}
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
                {{ getCellValue(item, column) }}
              </td>
              <td>
                <slot name="actions" :item="item">
                  <button class="btn btn-sm btn-outline-primary me-2" @click="$emit('edit', item)">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="$emit('delete', item)">
                    <i class="bi bi-trash"></i>
                  </button>
                </slot>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <nav v-if="totalPages > 1" class="mt-4">
        <ul class="pagination justify-content-center">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="$emit('page-change', currentPage - 1)">
              <i class="bi bi-chevron-left"></i>
            </a>
          </li>
          <li v-for="page in totalPages" :key="page" 
              class="page-item" 
              :class="{ active: currentPage === page }">
            <a class="page-link" href="#" @click.prevent="$emit('page-change', page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="$emit('page-change', currentPage + 1)">
              <i class="bi bi-chevron-right"></i>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.page-link {
  cursor: pointer;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
  opacity: 0.6;
}
</style> 