import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../lib/auth'
import LoginPage from '../components/LoginPage.vue'
import DashboardHome from '../components/DashboardHome.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/', name: 'dashboard', component: DashboardHome, meta: { requiresAuth: true } },
  // Add /idols, /tasks, /vote, /profile the same way as more HTML
  // screens get converted into components.
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    return { name: 'login' }
  }
  if (to.name === 'login' && isAuthenticated()) {
    return { name: 'dashboard' }
  }
})

export default router
