import { createRouter, createWebHistory } from 'vue-router'
import { hasAccessGranted } from '@/services/accessService'
import { hasBackendCredentials } from '@/services/authService'
import Home from '../views/Home.vue'

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
    component: Home
  },
  {
    path: '/menu',
    name: 'Menu',
    component: () => import('../views/Menu.vue')
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('../views/Cart.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue')
  },
  {
    path: '/order',
    name: 'Order',
    component: () => import('../views/Order.vue')
  },
  {
    path: '/order-history',
    name: 'OrderHistory',
    component: () => import('../views/OrderHistory.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  if (to.meta?.public) {
    return true
  }

  if (!hasAccessGranted() || !hasBackendCredentials()) {
    return {
      path: '/login',
      query: { redirect: to.fullPath }
    }
  }

  return true
})

export default router
