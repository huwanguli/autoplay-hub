<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTaskStore } from '@/stores/taskStore'

const taskStore = useTaskStore()
const route = useRoute()
const taskId = Number(route.params.id)

onMounted(() => {
  taskStore.fetchTask(taskId)
  taskStore.connectWebSocket()
})

onUnmounted(() => {
  taskStore.disconnectWebSocket()
})
</script>

<template>
  <div class="task-detail-view">
    <div v-if="taskStore.isLoading">正在加载任务详情...</div>
    <div v-if="taskStore.error" class="error-message">{{ taskStore.error }}</div>

    <!-- ★ 使用 v-if="taskStore.currentTask" 来确保对象存在才渲染 -->
    <div v-if="taskStore.currentTask" class="task-container">
      <div class="task-header">
        <h1>任务详情 (ID: {{ taskStore.currentTask.id }})</h1>
        <div
          v-if="taskStore.currentTask.status"
          class="status"
          :class="taskStore.currentTask.status.toLowerCase()"
        >
          状态: {{ taskStore.currentTask.status }}
        </div>
      </div>

      <div class="content-grid">
        <div class="log-panel">
          <h2>实时日志</h2>
          <pre class="log-box">{{ taskStore.currentTask.log || '等待任务开始...' }}</pre>
        </div>

        <div class="screenshot-panel">
          <h2>实时截图</h2>
          <div class="screenshot-box">
            <p v-if="!taskStore.currentTask.latest_screenshot_url">暂无截图</p>
            <!-- ★ 直接使用相对路径，Vite代理会自动处理 -->
            <img
              v-else
              :src="taskStore.currentTask.latest_screenshot_url"
              :key="taskStore.currentTask.latest_screenshot_url"
              alt="任务截图"
            />
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="!taskStore.isLoading">没有找到任务数据。</div>
  </div>
</template>

<style scoped>
.task-detail-view {
  max-width: 1200px;
  margin: auto;
  padding: 2rem;
}
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.status {
  padding: 8px 16px;
  border-radius: 20px;
  color: white;
  font-weight: bold;
}
.status.running {
  background-color: #2196f3;
}
.status.success {
  background-color: #4caf50;
}
.status.failed {
  background-color: #f44336;
}
.status.pending {
  background-color: #ff9800;
}
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}
h2 {
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}
.log-box {
  background-color: #2d2d2d;
  color: #f1f1f1;
  padding: 1rem;
  border-radius: 5px;
  white-space: pre-wrap;
  word-wrap: break-word;
  height: 500px;
  overflow-y: auto;
}
.screenshot-box {
  border: 1px solid #ddd;
  border-radius: 5px;
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.screenshot-box img {
  max-width: 100%;
  height: auto;
}
.error-message {
  color: red;
}
</style>
