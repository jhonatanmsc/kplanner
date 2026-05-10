import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import BoardView from './views/BoardView.vue'
import LoginView from './views/LoginView.vue'
import AdminUsersView from './views/AdminUsersView.vue'
import { useAuthStore } from './stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { path: '/', component: HomeView, meta: { requiresAuth: true } },
    { path: '/board/:id', component: BoardView, meta: { requiresAuth: true } },
    { path: '/admin/users', component: AdminUsersView, meta: { requiresAuth: true, requiresAdmin: true } },
  ],
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('auth_token')
  const auth = useAuthStore()
  const authNotRequired = to.path === '/login'

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (authNotRequired && token) {
    return next('/')
  }

  if (token && !auth.user) {
    try {
      await auth.fetchCurrentUser()
    } catch {
      return next('/login')
    }
  }

  if (to.meta.requiresAdmin && (!auth.user || !auth.user.is_admin)) {
    return next('/')
  }

  next()
})

export default router
