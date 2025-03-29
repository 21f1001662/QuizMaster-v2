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
    label: 'Average Percentage',
    backgroundColor: [
      'rgba(54, 162, 235, 0.6)',
      'rgba(255, 99, 132, 0.6)',
      'rgba(75, 192, 192, 0.6)',
      'rgba(255, 206, 86, 0.6)',
      'rgba(153, 102, 255, 0.6)'
    ],
    data: []
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
      position: 'top',
      align: 'center',
      labels: {
        boxWidth: 12,
        usePointStyle: true,
        pointStyle: 'rectRounded'
      }
    },
    title: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
      ticks: {
        callback: function(value) {
          return value + '%'
        }
      },
      grid: {
        display: true
      }
    },
    x: {
      grid: {
        display: true
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
    subjectChartData.value.datasets[0].data = response.data.subject_performance.map(s => Number(s.average_percentage.toFixed(2)))

    // Reverse the arrays to show latest points on the right
    performanceChartData.value.labels = response.data.recent_performance.map(p => 
      new Date(p.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    ).reverse()
    performanceChartData.value.datasets[0].data = response.data.recent_performance.map(p => Number(p.score_percentage.toFixed(2))).reverse()
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
    <!-- Summary Cards -->
    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="stat-card">
          <div class="stat-icon bg-primary">
            <i class="bi bi-pencil-square"></i>
          </div>
          <div class="stat-details">
            <h3>{{ stats?.total_quizzes_attempted || 0 }}</h3>
            <p>Quizzes Attempted</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="stat-card">
          <div class="stat-icon bg-info">
            <i class="bi bi-calendar-event"></i>
          </div>
          <div class="stat-details">
            <h3>{{ stats?.total_upcoming_quizzes || 0 }}</h3>
            <p>Upcoming Quizzes</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="stat-card">
          <div class="stat-icon">
            <div class="progress-circle" :style="{ 
              '--progress': `${(stats?.average_score_percentage || 0).toFixed(1)}%`,
              '--color': stats?.average_score_percentage >= 70 ? '#198754' : 
                        stats?.average_score_percentage >= 35 ? '#f9c924' : '#dc3545'
            }">
              <svg viewBox="0 0 36 36">
                <path 
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#e9ecef"
                  stroke-width="3"
                />
                <path 
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="var(--color)"
                  stroke-width="3"
                  :stroke-dasharray="`${stats?.average_score_percentage || 0}, 100`"
                />
              </svg>
              <div class="progress-emoji">
                {{ stats?.average_score_percentage >= 70 ? '🎉' : 
                   stats?.average_score_percentage >= 35 ? '👍' : '😢' }}
              </div>
            </div>
          </div>
          <div class="stat-details">
            <h3>{{ (stats?.average_score_percentage || 0).toFixed(1) }}%</h3>
            <p>Overall Performance</p>
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
            <div class="chart-container">
              <Bar 
                v-if="!loading" 
                :data="subjectChartData" 
                :options="subjectChartOptions"
                :height="300"
              />
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
                        {{ subject.average_percentage.toFixed(2) }}%
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
                        {{ quiz.score_percentage.toFixed(2) }}%
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
  width: 48px;
  height: 48px;
}

.progress-circle svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.progress-circle path {
  transition: stroke-dasharray 0.5s ease;
}

.progress-circle path:last-child {
  stroke-linecap: round;
}

.progress-emoji {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2rem;
  line-height: 1;
}

.stat-icon .progress-circle {
  margin: 0;
}

.chart-container {
  position: relative;
  margin: auto;
  height: 300px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon i {
  font-size: 1.5rem;
  color: white;
}

.stat-details h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.2;
}

.stat-details p {
  color: #6c757d;
  margin: 0;
  font-size: 0.9rem;
}
</style>