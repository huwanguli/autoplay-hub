import { createRouter, createWebHistory } from 'vue-router'
import AutomationHubView from '../views/AutomationHubView.vue'
import TaskDetailView from '@/views/TaskDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: AutomationHubView,
    },

    {
      path: '/tasks/:id',
      name: 'task-detail',
      component: TaskDetailView,
    },
  ],
})

export default router
