<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTaskDetailStore } from '@/stores/taskDetailStore'
import { storeToRefs } from 'pinia'

// --- 1. 初始化 ---
const route = useRoute() // 获取当前路由信息，主要是为了拿到URL中的任务ID
const taskDetailStore = useTaskDetailStore()
const taskId = route.params.id // 从URL中解析出任务ID，例如 /tasks/5 -> 5

// --- 2. 状态链接 ---
const { task, isLoading, error } = storeToRefs(taskDetailStore)

// --- 3. 生命周期钩子 ---
onMounted(async () => {
  // 当组件加载后，先从API获取任务的初始数据
  await taskDetailStore.fetchTask(taskId)
  // 然后，建立WebSocket连接以接收实时更新
  taskDetailStore.connectWebSocket()
})

onUnmounted(() => {
  // 当组件被销毁时（例如用户离开这个页面），断开WebSocket并清理数据
  taskDetailStore.disconnectWebSocket()
  taskDetailStore.clearTask()
})
</script>

<template>
  <div class="task-detail-container">
    <div v-if="isLoading">正在加载任务详情...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="task">
      <h1>任务 #{{ task.id }} 详情</h1>

      <div class="details-grid">
        <div><strong>脚本名称:</strong> {{ task.script_name }}</div>
        <div>
          <strong>状态:</strong>
          <span :class="`status-${task.status.toLowerCase()}`">{{ task.status }}</span>
        </div>
        <div><strong>创建时间:</strong> {{ new Date(task.created_at).toLocaleString() }}</div>
        <div>
          <strong>完成时间:</strong>
          {{ task.completed_at ? new Date(task.completed_at).toLocaleString() : 'N/A' }}
        </div>
      </div>

      <div class="main-content">
        <!-- 左侧：实时日志 -->
        <div class="log-panel">
          <h2>实时日志</h2>
          <pre class="log-box">{{ task.log || '等待任务开始...' }}</pre>
        </div>

        <!-- 右侧：最新截图 -->
        <div class="screenshot-panel">
          <div class="penel-header">
            <h2>最新截图</h2>
            <button
              @click="taskDetailStore.triggerScreenshot"
              :disabled="task.status !== 'RUNNING'"
              class="screenshot-btn"
            >
              实时快照
            </button>
          </div>
          <div class="screenshot-box">
            <img
              v-if="task.latest_screenshot_url"
              :src="task.latest_screenshot_url"
              alt="最新任务截图"
            />
            <div v-else class="no-screenshot">暂无截图</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-detail-container {
  max-width: 1200px;
  margin: auto;
}
h1 {
  margin-bottom: 1rem;
}
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}
.status-running {
  color: #007bff;
  font-weight: bold;
}
.status-success {
  color: #28a745;
  font-weight: bold;
}
.status-failed {
  color: #dc3545;
  font-weight: bold;
}
.status-pending {
  color: #6c757d;
  font-weight: bold;
}

.main-content {
  display: flex;
  gap: 2rem;
}
.log-panel {
  flex: 2;
}
.screenshot-panel {
  flex: 1;
}

.log-box {
  background-color: #212529;
  color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  height: 500px;
  overflow-y: auto;
  white-space: pre-wrap; /* 自动换行 */
  word-wrap: break-word;
}
.screenshot-box {
  border: 1px solid #ddd;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
}
img {
  max-width: 100%;
  height: auto;
}
.no-screenshot {
  color: #6c757d;
}
.error {
  color: #dc3545;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-header h2 {
  margin: 0;
  padding: 0;
  border: none;
}

.screenshot-btn {
  background-color: #17a2b8;
}

.screenshot-btn:hover {
  background-color: #117a8b;
}

.screenshot-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
