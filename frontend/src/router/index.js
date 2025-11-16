import { createRouter, createWebHistory } from 'vue-router'
import AutomationHubView from '../views/AutomationHubView.vue'
import TaskDetailView from '@/views/TaskDetailView.vue'
import ScriptManageView from '../views/ScriptManageView.vue'
import TaskHistoryView from '@/views/TaskHistoryView.vue'
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

    {
      path: '/scripts/manage',
      name: 'script-manage',
      component: ScriptManageView,
    },

    {
      path: '/tasks',
      name: 'task-history',
      component: TaskHistoryView,
    },
  ],
})

export default router
