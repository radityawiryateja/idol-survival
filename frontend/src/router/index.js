import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../lib/auth'
import LoginPage from '../components/LoginPage.vue'
import TelegramCallback from '../components/TelegramCallback.vue'
import DashboardHome from '../components/DashboardHome.vue'
import IdolsList from '../components/IdolsList.vue'
import Leaderboard from '../components/Leaderboard.vue'
import TasksPage from '../components/TasksPage.vue'
import ProfilePage from '../components/ProfilePage.vue'
import IdCardPage from '../components/IdCardPage.vue'
import RewardsPage from '../components/RewardsPage.vue'
import ShopPage from '../components/ShopPage.vue'
import TalksPage from '../components/TalksPage.vue'
import EventsPage from '../components/EventsPage.vue'
import VotePage from '../components/VotePage.vue'
import AccountSettingsPage from '../components/AccountSettingsPage.vue'
import NotificationSettingsPage from '../components/NotificationSettingsPage.vue'
import AppearanceSettingsPage from '../components/AppearanceSettingsPage.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/auth/telegram/callback', name: 'telegram-callback', component: TelegramCallback },
  { path: '/', name: 'dashboard', component: DashboardHome, meta: { requiresAuth: true } },
  { path: '/idols', name: 'idols', component: IdolsList },
  { path: '/leaderboard', name: 'leaderboard', component: Leaderboard },
  { path: '/tasks', name: 'tasks', component: TasksPage },
  { path: '/profile', name: 'profile', component: ProfilePage, meta: { requiresAuth: true } },
  { path: '/idols/:id/card', name: 'idol-card', component: IdCardPage },
  { path: '/rewards', name: 'rewards', component: RewardsPage },
  { path: '/shop', name: 'shop', component: ShopPage },
  { path: '/talk', name: 'talk', component: TalksPage },
  { path: '/events', name: 'events', component: EventsPage },
  { path: '/vote', name: 'vote', component: VotePage },
  { path: '/settings/account', name: 'settings-account', component: AccountSettingsPage, meta: { requiresAuth: true } },
  { path: '/settings/notifications', name: 'settings-notifications', component: NotificationSettingsPage, meta: { requiresAuth: true } },
  { path: '/settings/appearance', name: 'settings-appearance', component: AppearanceSettingsPage, meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' }
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
