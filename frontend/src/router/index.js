import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/sessions',
    name: 'SessionList',
    component: () => import('../views/SessionList.vue')
  },
  {
    path: '/sessions/:id',
    name: 'SessionDetail',
    component: () => import('../views/SessionDetail.vue')
  },
  {
    path: '/validation',
    name: 'SessionValidation',
    component: () => import('../views/SessionValidation.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
