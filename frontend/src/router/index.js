import { createRouter, createWebHistory } from 'vue-router'
import AdminLogin from '../views/admin/Login.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import Quizzes from '../views/admin/Quizzes.vue'
import Subjects from '../views/admin/Subjects.vue'
import Stats from '../views/admin/Stats.vue'
import Home from '../views/Home.vue'
import StudentLogin from '../views/student/Login.vue'
import StudentDashboard from '../views/student/Dashboard.vue'
import UpcomingQuizzes from '../views/student/UpcomingQuizzes.vue'
import CompletedQuizzes from '../views/student/CompletedQuizzes.vue'
import StudentStats from '../views/student/Stats.vue'
import { validateAdminToken, validateStudentToken } from '../utils/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    beforeEnter: async (to, from, next) => {
      const adminToken = localStorage.getItem('adminToken')
      if (adminToken) {
        const isValid = await validateAdminToken(adminToken)
        if (isValid) {
          next('/admin/dashboard')
        } else {
          localStorage.removeItem('adminToken')
          localStorage.removeItem('adminUser')
          next()
        }
      } else {
        next()
      }
    }
  },
  {
    path: '/admin/dashboard',
    component: AdminDashboard,
    beforeEnter: async (to, from, next) => {
      const adminToken = localStorage.getItem('adminToken')
      if (!adminToken) {
        next('/admin/login')
      } else {
        const isValid = await validateAdminToken(adminToken)
        if (isValid) {
          next()
        } else {
          localStorage.removeItem('adminToken')
          localStorage.removeItem('adminUser')
          next('/admin/login')
        }
      }
    },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard/quizzes'
      },
      {
        path: 'quizzes',
        name: 'Quizzes',
        component: Quizzes
      },
      {
        path: 'subjects',
        name: 'Subjects',
        component: Subjects
      },
      {
        path: 'stats',
        name: 'Stats',
        component: Stats
      }
    ]
  },
  {
    path: '/student/login',
    name: 'StudentLogin',
    component: StudentLogin,
    beforeEnter: async (to, from, next) => {
      const studentToken = localStorage.getItem('studentToken')
      if (studentToken) {
        const isValid = await validateStudentToken(studentToken)
        if (isValid) {
          next('/student/dashboard/quizzes')
        } else {
          localStorage.removeItem('studentToken')
          localStorage.removeItem('studentUser')
          next()
        }
      } else {
        next()
      }
    }
  },
  {
    path: '/student/dashboard',
    component: StudentDashboard,
    beforeEnter: async (to, from, next) => {
      const studentToken = localStorage.getItem('studentToken')
      if (!studentToken) {
        next('/student/login')
      } else {
        const isValid = await validateStudentToken(studentToken)
        if (isValid) {
          next()
        } else {
          localStorage.removeItem('studentToken')
          localStorage.removeItem('studentUser')
          next('/student/login')
        }
      }
    },
    children: [
      {
        path: 'quizzes',
        name: 'UpcomingQuizzes',
        component: UpcomingQuizzes
      },
      {
        path: 'quizzes/completed',
        name: 'CompletedQuizzes',
        component: CompletedQuizzes
      },
      {
        path: 'stats',
        name: 'StudentStats',
        component: StudentStats
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 