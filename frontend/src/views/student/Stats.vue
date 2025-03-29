<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import axios from 'axios'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js'
import { Bar, Line } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend)

const toast = useToast()
const loading = ref(false)
const stats = ref(null)

// Chart data
const subjectChartData = ref({
  labels: [],
  datasets: [{
    label: 'Average Score (%)',
    data: [],
    backgroundColor: '#0d6efd',
    borderRadius: 6
  }]
})

const performanceChartData = ref({
  labels: [],
  datasets: [{
    label: 'Score (%)',
    data: [],
    borderColor: '#198754',
    backgroundColor: 'rgba(25, 135, 84, 0.1)',
    tension: 0.4,
    fill: true
  }]
})

// Chart options
const subjectChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      grid: {
        display: false
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

const performanceChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      grid: {
        display: false
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

// Fetch stats
const fetchStats = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('studentToken')
    const response = await axios.get('http://localhost:5000/api/stats', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    stats.value = response.data

    // Update chart data
    subjectChartData.value.labels = response.data.subject_performance.map(s => s.subject_name)
    subjectChartData.value.datasets[0].data = response.data.subject_performance.map(s => Number(s.average_percentage.toFixed(1)))

    performanceChartData.value.labels = response.data.recent_performance.map(p => 
      new Date(p.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    )
    performanceChartData.value.datasets[0].data = response.data.recent_performance.map(p => Number(p.score_percentage.toFixed(1)))
  } catch (err) {
    toast.error('Failed to fetch statistics')
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Performance Statistics</h2>
      <div class="d-flex gap-3">
        <div class="text-center">
          <div class="h4 mb-0">{{ stats?.total_quizzes_attempted || 0 }}</div>
          <div class="text-muted small">Quizzes Attempted</div>
        </div>
        <div class="text-center">
          <div class="h4 mb-0">{{ stats?.total_upcoming_quizzes || 0 }}</div>
          <div class="text-muted small">Upcoming Quizzes</div>
        </div>
      </div>
    </div>

    <!-- Overall Performance -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="d-flex align-items-center">
          <div class="flex-grow-1">
            <h6 class="text-muted mb-1">Overall Performance</h6>
            <div class="h3 mb-0">{{ (stats?.average_score_percentage || 0).toFixed(1) }}%</div>
          </div>
          <div class="progress-circle" :style="{ 
            '--progress': `${(stats?.average_score_percentage || 0).toFixed(1)}%`,
            '--color': stats?.average_score_percentage >= 70 ? '#198754' : 
                      stats?.average_score_percentage >= 35 ? '#ffc107' : '#dc3545'
          }">
            <svg viewBox="0 0 36 36">
              <path d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="#e9ecef"
                stroke-width="3"
              />
              <path d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="var(--color)"
                stroke-width="3"
                stroke-dasharray="var(--progress), 100"
              />
            </svg>
            <div class="progress-text">{{ (stats?.average_score_percentage || 0).toFixed(1) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Subject Performance -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title mb-4">Subject-wise Performance</h5>
            <div class="chart-container" style="height: 300px;">
              <Bar v-if="!loading" :data="subjectChartData" :options="subjectChartOptions" />
              <div v-else class="d-flex align-items-center justify-content-center h-100">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title mb-4">Subject Details</h5>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Subject</th>
                    <th>Score</th>
                    <th>Quizzes</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subject in stats?.subject_performance" :key="subject.subject_name">
                    <td>{{ subject.subject_name }}</td>
                    <td>
                      <span class="badge" :class="{
                        'bg-success': subject.average_percentage >= 70,
                        'bg-warning': subject.average_percentage >= 35 && subject.average_percentage < 70,
                        'bg-danger': subject.average_percentage < 35
                      }">
                        {{ subject.average_percentage.toFixed(1) }}%
                      </span>
                    </td>
                    <td>{{ subject.quizzes_taken }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Performance -->
    <div class="row">
      <div class="col-md-8">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title mb-4">Recent Performance Trend</h5>
            <div class="chart-container" style="height: 300px;">
              <Line v-if="!loading" :data="performanceChartData" :options="performanceChartOptions" />
              <div v-else class="d-flex align-items-center justify-content-center h-100">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title mb-4">Recent Quizzes</h5>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Quiz</th>
                    <th>Date</th>
                    <th>Score</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="quiz in stats?.recent_performance" :key="quiz.date">
                    <td>{{ quiz.quiz_name }}</td>
                    <td>{{ new Date(quiz.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}</td>
                    <td>
                      <span class="badge" :class="{
                        'bg-success': quiz.score_percentage >= 70,
                        'bg-warning': quiz.score_percentage >= 35 && quiz.score_percentage < 70,
                        'bg-danger': quiz.score_percentage < 35
                      }">
                        {{ quiz.score_percentage.toFixed(1) }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  background: #fff;
}

.card-title {
  color: #2c3e50;
  font-weight: 600;
}

.table {
  margin-bottom: 0;
}

.table th {
  font-weight: 600;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
}

.table td {
  vertical-align: middle;
  border-bottom: 1px solid #dee2e6;
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.badge {
  padding: 0.5em 0.8em;
  font-weight: 500;
}

.progress-circle {
  position: relative;
  width: 80px;
  height: 80px;
}

.progress-circle svg {
  transform: rotate(-90deg);
}

.progress-circle path {
  transition: stroke-dasharray 0.5s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color);
}

.chart-container {
  position: relative;
  margin: auto;
  height: 300px;
}
</style>