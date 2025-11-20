<script setup>
import { RouterLink } from 'vue-router'
// 1. 导入我们创建的 authStore
import { useAuthStore } from '@/stores/authStore'

// 2. 获取 authStore 的实例
const authStore = useAuthStore()
</script>

<template>
  <aside class="sidebar">
    <!-- 导航部分 (保持不变) -->
    <nav class="navigation">
      <ul>
        <li>
          <RouterLink to="/" class="nav-link">
            <span class="icon">🏠</span>
            <span class="text">仪表盘 (运行脚本)</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/scripts/manage" class="nav-link">
            <span class="icon">📝</span>
            <span class="text">脚本管理</span>
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/tasks" class="nav-link">
            <span class="icon">📊</span>
            <span class="text">任务历史</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- ★ 新增：用户 Profile 区域 ★ -->
    <div class="user-profile">
      <div v-if="authStore.isAuthenticated" class="profile-content">
        <span class="icon">👤</span>
        <div class="user-info">
          <span class="greeting">欢迎,</span>
          <span class="username">{{ authStore.user.username }}</span>
        </div>
        <button @click="authStore.logout()" class="logout-btn" title="登出">
          <span class="icon">➔</span>
        </button>
      </div>
      <div v-else class="profile-content">
        <span class="icon">👻</span>
        <div class="user-info">
          <span class="greeting">游客模式</span>
        </div>
        <router-link to="/login" class="login-link"> 登录/注册 </router-link>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  background-color: #343a40;
  color: #fff;
  display: flex;
  flex-direction: column; /* 让导航和profile垂直排列 */
  justify-content: space-between; /* 将profile推到底部 */
  height: 100vh;
}

.navigation ul {
  list-style: none;
  padding: 0;
  margin: 0;
  padding-top: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.8rem 1.5rem;
  color: #adb5bd;
  text-decoration: none;
  transition:
    background-color 0.2s,
    color 0.2s;
  font-size: 0.95rem;
}

.nav-link:hover {
  background-color: #495057;
  color: #fff;
}

.router-link-exact-active {
  background-color: #007bff;
  color: #fff;
  font-weight: bold;
}

.icon {
  margin-right: 1rem;
  font-size: 1.2rem;
}

/* ★ 新增：用户 Profile 区域的样式 ★ */
.user-profile {
  padding: 1rem 1.5rem;
  border-top: 1px solid #495057;
}

.profile-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.greeting {
  font-size: 0.8rem;
  color: #adb5bd;
}

.username {
  font-weight: bold;
  color: #fff;
}

.logout-btn {
  background: none;
  border: 1px solid #dc3545;
  color: #dc3545;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logout-btn:hover {
  background-color: #dc3545;
  color: white;
}

.login-link {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  text-align: center;
}
</style>
