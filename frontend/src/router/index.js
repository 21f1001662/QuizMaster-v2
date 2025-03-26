import { createRouter, createWebHistory } from 'vue-router'
import AdminLogin from '../views/admin/Login.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import Quizzes from '../views/admin/Quizzes.vue'
import Subjects from '../views/admin/Subjects.vue'
import Stats from '../views/admin/Stats.vue'
import Home from '../views/Home.vue'
import { validateAdminToken } from '../utils/auth'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 