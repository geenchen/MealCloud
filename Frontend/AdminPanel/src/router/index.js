import { createRouter, createWebHistory } from 'vue-router'
import TableDashboard from '../components/TableDashboard.vue'
import Home from '../views/Home.vue'
import { isAuthenticated } from '../services/authService'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/dishes',
    name: 'Dishes',
    component: () => import('../views/Dishes.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/Categories.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/Orders.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tables',
    name: 'Tables',
    component: () => import('../views/Tables.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/table-dashboard',
    name: 'TableDashboard',
    component: TableDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/order-entry',
    name: 'OrderEntry',
    component: () => import('../views/OrderEntry.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/special-functions',
    name: 'SpecialFunctions',
    component: () => import('../views/SpecialFunctions.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.public) {
    if (to.path === '/login' && isAuthenticated()) {
      next('/')
      return
    }
    next()
    return
  }

  if (to.meta.requiresAuth && !isAuthenticated()) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  next()
})

export default router
