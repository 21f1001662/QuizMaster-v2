<script setup>
import { useRouter } from 'vue-router'
import { onMounted, computed } from 'vue'
import { validateAdminToken, validateStudentToken } from '../utils/auth'

const router = useRouter()

const currentYear = computed(() => new Date().getFullYear())

onMounted(async () => {
  // Check for admin token
  const adminToken = localStorage.getItem('adminToken')
  if (adminToken) {
    const isValid = await validateAdminToken(adminToken)
    if (isValid) {
      router.push('/admin/dashboard')
      return
    } else {
      localStorage.removeItem('adminToken')
      localStorage.removeItem('adminUser')
    }
  }

  // Check for student token
  const studentToken = localStorage.getItem('studentToken')
  if (studentToken) {
    const isValid = await validateStudentToken(studentToken)
    if (isValid) {
      router.push('/student/dashboard/quizzes')
    } else {
      localStorage.removeItem('studentToken')
      localStorage.removeItem('studentUser')
    }
  }
})
</script>

<template>
  <div class="landing-page">
    <!-- Floating Shapes -->
    <div class="floating-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="shape shape-4"></div>
    </div>

    <!-- Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="display-4 fw-bold mb-4">Welcome to <span class="gradient-text">QuizMaster</span></h1>
          <p class="lead mb-4">A modern platform for creating and attempting quizzes with advanced features and real-time analytics.</p>
          <div class="hero-buttons">
            <router-link to="/student/login" class="btn btn-primary btn-lg">
              <i class="bi bi-pencil-square me-2"></i>Attempt Quiz
            </router-link>
            <router-link to="/admin/login" class="btn btn-glass btn-lg">
              <i class="bi bi-plus-circle me-2"></i>Create Quiz
            </router-link>
          </div>
        </div>
        <div class="hero-image">
          <div class="icon-wrapper">
            <i class="bi bi-journal-check"></i>
            <div class="glow"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-number">1000+</div>
          <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">500+</div>
          <div class="stat-label">Quizzes Created</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">50+</div>
          <div class="stat-label">Subjects</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">24/7</div>
          <div class="stat-label">Support</div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <h2 class="text-center mb-2">Powerful Features</h2>
      <p class="text-center text-muted mb-5">Everything you need to create and manage quizzes effectively</p>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-check2-square text-primary"></i>
          </div>
          <h3>Multiple Question Types</h3>
          <p>Support for both MCQ and Numeric questions with flexible marking schemes</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-robot text-success"></i>
          </div>
          <h3>AI Question Generation</h3>
          <p>Automatically generate questions based on context using advanced AI</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-book text-info"></i>
          </div>
          <h3>Subject & Chapter Based</h3>
          <p>Organize quizzes by subjects and chapters for structured learning</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-envelope text-warning"></i>
          </div>
          <h3>Email Notifications</h3>
          <p>Stay updated with quiz schedules and results via email notifications</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-file-earmark-excel text-success"></i>
          </div>
          <h3>Result Export</h3>
          <p>Export quiz results in various formats for detailed analysis</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-graph-up text-danger"></i>
          </div>
          <h3>Post-Quiz Analysis</h3>
          <p>Comprehensive analytics and insights after quiz completion</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-shield-check text-primary"></i>
          </div>
          <h3>Enhanced Security</h3>
          <p>Secure authentication and data protection for all users</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-clock-history text-info"></i>
          </div>
          <h3>Progress Tracking</h3>
          <p>Monitor student performance and learning progress over time</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="bi bi-bar-chart-line text-purple"></i>
          </div>
          <h3>View Detailed Statistics</h3>
          <p>Access comprehensive performance metrics, trends, and comparative analysis</p>
        </div>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="how-it-works-section">
      <h2 class="text-center mb-2">How It Works</h2>
      <p class="text-center text-muted mb-5">Simple steps to get started with QuizMaster</p>
      <div class="steps-grid">
        <div class="step-card">
          <div class="step-number">1</div>
          <h4>Create Account</h4>
          <p>Log in as a teacher to create quizzes or as a student to attempt them</p>
        </div>
        <div class="step-card">
          <div class="step-number">2</div>
          <h4>Select Subject</h4>
          <p>Choose from various subjects and chapters or create your own</p>
        </div>
        <div class="step-card">
          <div class="step-number">3</div>
          <h4>Create/Attempt Quiz</h4>
          <p>Create engaging quizzes or attempt them to test your knowledge</p>
        </div>
        <div class="step-card">
          <div class="step-number">4</div>
          <h4>View Results</h4>
          <p>Get detailed analysis and insights about your performance</p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <p class="mb-0">&copy; {{ currentYear }} QuizMaster. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  background: #ffffff;
}

/* Floating Shapes */
.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.shape {
  position: absolute;
  background: linear-gradient(45deg, rgba(13, 110, 253, 0.1), rgba(116, 209, 234, 0.1));
  border-radius: 50%;
  animation: float 20s infinite linear;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  left: -150px;
  animation-delay: -5s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  top: 60%;
  right: -100px;
  animation-delay: -10s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  bottom: 10%;
  left: 20%;
  animation-delay: -15s;
}

.shape-4 {
  width: 250px;
  height: 250px;
  top: 20%;
  right: 20%;
  animation-delay: -20s;
}

@keyframes float {
  0% {
    transform: rotate(0deg) translate(0, 0) scale(1);
  }
  33% {
    transform: rotate(120deg) translate(50px, 50px) scale(1.1);
  }
  66% {
    transform: rotate(240deg) translate(-50px, 50px) scale(0.9);
  }
  100% {
    transform: rotate(360deg) translate(0, 0) scale(1);
  }
}

.hero-section {
  background: linear-gradient(135deg, #f0f7ff 0%, #e5f0ff 50%, #edf7ff 100%);
  position: relative;
  padding: 8rem 2rem;
  flex: 1;
  display: flex;
  align-items: center;
  z-index: 1;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 150%, rgba(13, 110, 253, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 80% -50%, rgba(116, 209, 234, 0.08) 0%, transparent 50%);
  z-index: -1;
}

.gradient-text {
  background: linear-gradient(45deg, #0d6efd, #0091ff, #00b4d8);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  position: relative;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6rem;
  align-items: center;
}

.hero-text h1 {
  font-size: 3.5rem;
  line-height: 1.2;
  margin-bottom: 1.5rem;
}

.hero-text .lead {
  font-size: 1.25rem;
  color: #4a5568;
  margin-bottom: 2rem;
}

.hero-buttons {
  display: flex;
  gap: 1.5rem;
}

.hero-buttons .btn {
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.hero-buttons .btn-primary {
  background: linear-gradient(135deg, #0d6efd, #0a58ca);
  border: none;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.2);
}

.hero-buttons .btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(13, 110, 253, 0.3);
}

.hero-buttons .btn-glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #2c3e50;
}

.hero-buttons .btn-glass:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.icon-wrapper {
  width: 180px;
  height: 180px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: white;
  box-shadow: 0 8px 32px rgba(13, 110, 253, 0.15);
  position: relative;
  overflow: hidden;
}

.icon-wrapper i {
  font-size: 6rem;
  color: #0d6efd;
  z-index: 2;
}

.glow {
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at center, rgba(13, 110, 253, 0.2), transparent 70%);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.2;
  }
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
}

.stats-section {
  background: white;
  padding: 4rem 2rem;
  position: relative;
  z-index: 1;
  box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
}

.stats-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 3rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(45deg, #0d6efd, #0dcaf0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 0.75rem;
  line-height: 1;
}

.stat-label {
  font-size: 1.1rem;
  color: #4a5568;
  font-weight: 500;
}

.features-section {
  padding: 8rem 2rem;
  background: white;
}

.features-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2.5rem;
}

.feature-card {
  background: white;
  padding: 2.5rem;
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid rgba(0,0,0,0.05);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border-color: rgba(13, 110, 253, 0.1);
}

.feature-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
  background: linear-gradient(135deg, #e9ecef, #f8f9fa);
}

.feature-icon i {
  font-size: 2rem;
}

.feature-card h3 {
  color: #2c3e50;
  font-size: 1.25rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.feature-card p {
  color: #6c757d;
  margin: 0;
  line-height: 1.6;
}

.how-it-works-section {
  background: linear-gradient(135deg, #f0f7ff 0%, #e5f0ff 50%, #edf7ff 100%);
  padding: 8rem 2rem;
  position: relative;
  overflow: hidden;
}

.how-it-works-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 20%, rgba(13, 110, 253, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 20% 80%, rgba(116, 209, 234, 0.08) 0%, transparent 50%);
  z-index: 0;
}

.steps-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2.5rem;
  position: relative;
  z-index: 1;
}

.steps-grid::after {
  content: '';
  position: absolute;
  top: 60px;
  left: 100px;
  right: 100px;
  height: 2px;
  z-index: -1;
}

.step-card {
  background: white;
  padding: 2.5rem;
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  position: relative;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.step-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(13, 110, 253, 0.15);
  border-color: rgba(13, 110, 253, 0.2);
}

.step-number {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #0d6efd, #0091ff);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.25rem;
  margin: 0 auto 1.5rem;
  position: relative;
  z-index: 2;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.2);
}

.step-card h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-weight: 600;
  font-size: 1.25rem;
}

.step-card p {
  color: #4a5568;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

.footer {
  background: #f8f9fa;
  padding: 2rem;
  text-align: center;
  color: #4a5568;
  border-top: 1px solid rgba(0,0,0,0.05);
}

@media (max-width: 768px) {
  .hero-section {
    padding: 6rem 2rem;
  }

  .hero-content {
    grid-template-columns: 1fr;
    gap: 4rem;
    text-align: center;
  }

  .hero-text h1 {
    font-size: 2.75rem;
  }

  .hero-buttons {
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  .stat-item {
    background: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.05);
  }

  .stat-number {
    font-size: 2.5rem;
  }

  .steps-grid::after {
    display: none;
  }
  
  .steps-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 4rem 1.5rem;
  }

  .hero-content {
    display: flex;
    flex-direction: column-reverse;
    gap: 3rem;
  }

  .hero-text h1 {
    font-size: 2.25rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .stat-item {
    padding: 1rem;
  }

  .stat-number {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  .stat-label {
    font-size: 0.9rem;
  }

  .hero-buttons {
    flex-direction: column;
    gap: 1rem;
  }

  .hero-buttons .btn {
    width: 100%;
  }

  .features-section, .how-it-works-section {
    padding: 4rem 1.5rem;
  }

  .steps-grid {
    grid-template-columns: 1fr;
  }
  
  .step-card {
    max-width: 320px;
    margin: 0 auto;
  }
}

.text-purple {
  color: #6f42c1;
}
</style> 