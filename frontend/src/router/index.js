import { createRouter, createWebHistory } from 'vue-router'
import AdminLogin from '../views/admin/Login.vue'
import AdminDashboard from '../views/admin/Dashboard.vue'
import Quizzes from '../views/admin/Quizzes.vue'
import Subjects from '../views/admin/Subjects.vue'
import Stats from '../views/admin/Stats.vue'

const routes = [
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin
  },
  {
    path: '/admin/dashboard',
    component: AdminDashboard,
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
  },
  {
    path: '/',
    redirect: '/admin/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 