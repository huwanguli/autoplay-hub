import { createRouter, createWebHistory } from 'vue-router'
import AutomationHubView from '../views/AutomationHubView.vue'
import TaskDetailView from '../views/TaskDetailView.vue'
import ScriptManageView from '../views/ScriptManageView.vue' // 保持您已有的路由
import TaskHistoryView from '../views/TaskHistoryView.vue'
import LoginView from '../views/LoginView.vue' // 新增
import RegisterView from '../views/RegisterView.vue' // 新增

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
      props: true, // 建议开启props，让组件解耦
    },
    // ★ 修正：保留您已有的脚本管理页面路由
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
    // ★ 新增：认证相关路由
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
  ],
})

// ★ 新增：路由守卫（保持不变，逻辑是正确的）
// 它的作用是，如果您未来想保护某些页面，可以在这里添加逻辑
router.beforeEach((to, from, next) => {
  // const authStore = useAuthStore();
  // const publicPages = ['/login', '/register'];
  // const authRequired = !publicPages.includes(to.path);
  // if (authRequired && !authStore.isAuthenticated) {
  //   return next('/login');
  // }
  next()
})

export default router
