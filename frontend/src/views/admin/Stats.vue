<template>
  <div class="container-fluid p-4">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="dashboard">
      <!-- Summary Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-primary">
              <i class="bi bi-people-fill"></i>
            </div>
            <div class="stat-details">
              <h3>{{ stats.total_users }}</h3>
              <p>Total Users</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-success">
              <i class="bi bi-journal-check"></i>
            </div>
            <div class="stat-details">
              <h3>{{ stats.total_quizzes }}</h3>
              <p>Total Quizzes</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-info">
              <i class="bi bi-pencil-square"></i>
            </div>
            <div class="stat-details">
              <h3>{{ stats.total_attempts }}</h3>
              <p>Total Attempts</p>
            </div>
          </div>
        </div>
        
        <div class="col-md-3">
          <div class="stat-card">
            <div class="stat-icon bg-warning">
              <i class="bi bi-graph-up"></i>
            </div>
            <div class="stat-details">
              <h3>{{ stats.total_average_percentage.toFixed(1) }}%</h3>
              <p>Average Score</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div class="row g-4">
        <div class="col-md-8">
          <div class="chart-card">
            <Bar 
              :data="subjectChartData" 
              :options="barOptions"
              :height="300"
            />
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="chart-card">
            <Doughnut 
              :data="quizAttemptsData" 
              :options="doughnutOptions"
              :height="300"
            />
          </div>
        </div>
      </div>

      <!-- Top Attempted Quizzes Table -->
      <div class="row mt-4">
        <div class="col-12">
          <div class="table-card">
            <h3 class="card-title mb-4">Top Attempted Quizzes</h3>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Quiz Name</th>
                    <th>Subject</th>
                    <th>Chapter</th>
                    <th>Total Attempts</th>
                    <th>Average Score</th>
                    <th>Success Rate</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="quiz in stats.top_attempted_quizzes" :key="quiz.quiz_id">
                    <td>{{ quiz.quiz_name }}</td>
                    <td>{{ quiz.subject_name }}</td>
                    <td>{{ quiz.chapter_name }}</td>
                    <td>{{ quiz.total_attempts }}</td>
                    <td>{{ quiz.average_score.toFixed(1) }}/{{ quiz.total_score }}</td>
                    <td>
                      <div class="progress" style="height: 20px;">
                        <div 
                          class="progress-bar" 
                          role="progressbar"
                          :style="{ width: quiz.average_percentage + '%' }"
                          :class="{
                            'bg-danger': quiz.average_percentage < 40,
                            'bg-warning': quiz.average_percentage >= 40 && quiz.average_percentage < 70,
                            'bg-success': quiz.average_percentage >= 70
                          }"
                        >
                          {{ quiz.average_percentage.toFixed(1) }}%
                        </div>
                      </div>
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

<script setup>
import { ref, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement } from 'chart.js'
import axios from 'axios'

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

const stats = ref(null)
const loading = ref(true)

// Chart options
const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: true,
      text: 'Subject-wise Performance'
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
      }
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: true,
      text: 'Top Attempted Quizzes Distribution'
    }
  }
}

// Computed chart data
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

const quizAttemptsData = ref({
  labels: [],
  datasets: [{
    data: [],
    backgroundColor: [
      'rgba(54, 162, 235, 0.8)',
      'rgba(255, 99, 132, 0.8)',
      'rgba(75, 192, 192, 0.8)',
      'rgba(255, 206, 86, 0.8)',
      'rgba(153, 102, 255, 0.8)'
    ]
  }]
})

const fetchStats = async () => {
  try {
    const token = localStorage.getItem('adminToken')
    const response = await axios.get('http://localhost:5000/api/admin/stats', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    stats.value = response.data
    
    // Update subject chart data
    subjectChartData.value.labels = response.data.subject_wise_scores.map(s => s.subject_name)
    subjectChartData.value.datasets[0].data = response.data.subject_wise_scores.map(s => s.average_percentage)
    
    // Update quiz attempts chart data
    quizAttemptsData.value.labels = response.data.top_attempted_quizzes.map(q => q.quiz_name)
    quizAttemptsData.value.datasets[0].data = response.data.top_attempted_quizzes.map(q => q.total_attempts)
    
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
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

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  height: 100%;
}

.table-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card-title {
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
}

.table th {
  font-weight: 600;
  color: #2c3e50;
  border-bottom-width: 2px;
}

.table td {
  vertical-align: middle;
}

.progress {
  border-radius: 10px;
  background-color: #f8f9fa;
}

.progress-bar {
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 0.85rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .stat-card {
    padding: 1rem;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  
  .stat-details h3 {
    font-size: 1.25rem;
  }
  
  .chart-card, .table-card {
    padding: 1rem;
  }
}
</style> 