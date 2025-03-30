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
            :placeholder="searchPlaceholder"
            :value="modelValue"
            @input="$emit('update:modelValue', $event.target.value); $emit('search', $event.target.value)"
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
  font-weight: 600;
  color: #6c757d;
  padding: 1rem;
  white-space: nowrap;
}

.table th.fw-bold {
  font-weight: 600 !important;
}

.table td {
  vertical-align: middle;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  white-space: nowrap;
}

.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  background: #fff;
  overflow: hidden;
}

.card-body {
  padding: 1.5rem;
}

.page-link {
  cursor: pointer;
  border: none;
  padding: 0.5rem 1rem;
  margin: 0 0.25rem;
  border-radius: 6px;
  color: #0d6efd;
  transition: all 0.2s ease;
}

.page-link:hover {
  background-color: #e9ecef;
  color: #0d6efd;
}

.page-item.active .page-link {
  background-color: #0d6efd;
  color: #fff;
}

.page-item.disabled .page-link {
  cursor: not-allowed;
  opacity: 0.6;
  color: #6c757d;
}

.cursor-pointer {
  cursor: pointer;
  transition: all 0.2s ease;
}

.cursor-pointer:hover {
  background-color: #f8f9fa;
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
  border-radius: 8px 0 0 8px;
}

.input-group .form-control {
  border-left: none;
  border-radius: 0 8px 8px 0;
}

.input-group .form-control:focus {
  border-color: #dee2e6;
  box-shadow: none;
}

.table-responsive {
  border-radius: 12px;
  overflow: hidden;
}

.table {
  margin-bottom: 0;
}

.table thead th:first-child {
  border-top-left-radius: 12px;
}

.table thead th:last-child {
  border-top-right-radius: 12px;
}

.table tbody tr:last-child td:first-child {
  border-bottom-left-radius: 12px;
}

.table tbody tr:last-child td:last-child {
  border-bottom-right-radius: 12px;
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.btn-primary {
  border-radius: 8px;
  padding: 0.5rem 1.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(13, 110, 253, 0.2);
}

.btn-sm {
  padding: 0.4rem 0.8rem;
  font-size: 0.875rem;
  border-radius: 6px;
}

.btn-outline-primary {
  border-width: 2px;
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(13, 110, 253, 0.1);
}

.btn-outline-danger {
  border-width: 2px;
  transition: all 0.2s ease;
}

.btn-outline-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.1);
}
</style> 