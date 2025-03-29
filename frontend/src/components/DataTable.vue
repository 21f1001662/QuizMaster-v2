<script setup>
const props = defineProps({
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
  },
  showCreateButton: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  searchQuery: {
    type: String,
    default: ''
  }
})

defineEmits(['search', 'create', 'edit', 'delete', 'update:modelValue', 'page-change', 'row-click'])

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
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="input-group" style="max-width: 300px;">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Search..."
            :value="searchQuery"
            @input="$emit('update:searchQuery', $event.target.value); $emit('search', $event.target.value)"
          >
        </div>
        <slot name="headerActions"></slot>
      </div>

      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
      </div>

      <div v-else>
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th v-for="col in columns" :key="col.key" :class="{ 'fw-bold': col.key === 'name' }">
                  <div class="d-flex align-items-center">
                    <i v-if="col.icon" :class="col.icon" class="me-2"></i>
                    {{ col.label }}
                  </div>
                </th>
                <th v-if="showActions">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in data" :key="index" @click="!showActions && $emit('row-click', item)" :class="{ 'cursor-pointer': !showActions }">
                <td v-for="col in columns" :key="col.key">
                  <slot :name="col.key" :item="item">
                    {{ getCellValue(item, col) }}
                  </slot>
                </td>
                <td v-if="showActions">
                  <slot name="actions" :item="item"></slot>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
          <nav>
            <ul class="pagination">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <a class="page-link" href="#" @click.prevent="$emit('page-change', currentPage - 1)">
                  <i class="bi bi-chevron-left"></i>
                </a>
              </li>
              <li v-for="page in totalPages" :key="page" class="page-item" :class="{ active: currentPage === page }">
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
    </div>
  </div>
</template>

<style scoped>
.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: bold;
  color: #6c757d;
}

.table th.fw-bold {
  font-weight: bold !important;
}

.table td {
  vertical-align: middle;
}

.card {
  border: none;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

.card-body {
  padding: 1.5rem;
}

.page-link {
  cursor: pointer;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
  opacity: 0.6;
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.input-group .form-control {
  border-left: none;
}

.input-group .form-control:focus {
  border-color: #dee2e6;
  box-shadow: none;
}
</style> 