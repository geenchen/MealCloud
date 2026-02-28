import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import TableDashboard from '../components/TableDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/dishes',
    name: 'Dishes',
    component: () => import('../views/Dishes.vue')
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/Orders.vue')
  },
  {
    path: '/tables',
    name: 'Tables',
    component: () => import('../views/Tables.vue')
  },
  {
    path: '/table-dashboard',
    name: 'TableDashboard',
    component: TableDashboard
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue')
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue')
  },
  {
    path: '/order-entry',
    name: 'OrderEntry',
    component: () => import('../views/OrderEntry.vue')
  },
  {
    path: '/special-functions',
    name: 'SpecialFunctions',
    component: () => import('../views/SpecialFunctions.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router