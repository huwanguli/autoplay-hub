<script setup>
import { RouterView } from 'vue-router'
// 导入我们新创建的侧边栏组件
import Sidebar from './components/Sidebar.vue'
</script>

<template>
  <div class="app-layout">
    <!-- 左侧：常驻的侧边栏 -->
    <Sidebar />

    <!-- 右侧：内容区 -->
    <div class="main-content-wrapper">
      <header class="main-header">
        <div class="wrapper">
          <h1>AutoPlay Hub</h1>
        </div>
      </header>

      <main class="content-area">
        <!-- 我们的所有页面都会在这个“插座”里显示 -->
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style>
:root {
  --sidebar-width: 250px;
  --header-height: 60px;
  --color-background: #f4f7f6;
  --color-text: #2c3e50;
}

body {
  margin: 0;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--color-background);
  color: var(--color-text);
}

.app-layout {
  display: flex;
}

.main-content-wrapper {
  flex-grow: 1; /* 占据剩余的所有空间 */
  display: flex;
  flex-direction: column;
  height: 100vh; /* 占满整个视口高度 */
}

.main-header {
  height: var(--header-height);
  line-height: var(--header-height);
  background-color: #fff;
  padding: 0 2rem;
  border-bottom: 1px solid #dee2e6;
  flex-shrink: 0; /* 防止头部被压缩 */
}

.main-header h1 {
  font-size: 1.5rem;
  font-weight: 500;
  margin: 0;
}

.content-area {
  padding: 2rem;
  overflow-y: auto; /* 如果内容超长，则内容区可以滚动，但侧边栏和头部不动 */
  flex-grow: 1;
}
</style>
