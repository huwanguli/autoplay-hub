<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <aside class="sidebar">
    <nav class="navigation">
      <ul>
        <li>
          <!-- RouterLink 是Vue中用于生成导航链接的组件，它比普通的<a>标签更高效 -->
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
  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  background-color: #343a40;
  color: #fff;
  padding-top: 1rem;
}

.navigation ul {
  list-style: none;
  padding: 0;
  margin: 0;
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

/* 这个特殊的 .router-link-exact-active 类是Vue Router自动添加的
   它会应用到当前正处于激活状态的链接上，非常智能！ */
.router-link-exact-active {
  background-color: #007bff;
  color: #fff;
  font-weight: bold;
}

.icon {
  margin-right: 1rem;
  font-size: 1.2rem;
}
</style>
