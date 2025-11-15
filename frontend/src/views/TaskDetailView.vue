<script setup>
import { onMounted, onUnmounted, nextTick, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useTaskStore } from '@/stores/taskStore'

// 1. 获取 store 实例和任务ID
const taskStore = useTaskStore()
const route = useRoute()
const taskId = Number(route.params.id)

// 2. ★ 关键改动：创建一个 ref 来强制组件更新
// 我们将通过改变这个 ref 的值来告诉Vue：“嘿，你需要重新渲染了！”
const forceUpdateKey = ref(0)

// 3. 在组件挂载时执行
onMounted(() => {
  // 清理旧数据并获取新数据
  taskStore.currentTask = {}
  taskStore.fetchTask(taskId)
  taskStore.connectWebSocket()

  // 4. ★ 关键改动：订阅 Pinia store 的 action
  // `$onAction` 会在 store 的任何一个 action 被调用后触发。
  const unsubscribe = taskStore.$onAction(({ name, store, after }) => {
    // 我们只关心 store 的数据是否被修改了
    // `after` 会在 action 执行成功后被调用
    after(() => {
      // 无论哪个 action 修改了 store，我们都手动触发一次视图更新
      console.log(`Action '${name}' finished, forcing component update.`)
      forceUpdateKey.value++ // 改变key的值，强制Vue重新渲染
    })
  })

  // 5. 在组件卸载时，取消订阅，防止内存泄漏
  onUnmounted(() => {
    taskStore.disconnectWebSocket()
    unsubscribe() // 调用 `onAction` 返回的函数来取消订阅
  })
})
</script>

<template>
  <!-- 6. ★ 关键改动：将 `forceUpdateKey` 作为组件根元素的 :key -->
  <!-- 当 key 的值改变时，Vue会认为这是一个全新的组件，从而强制重新渲染它。 -->
  <div class="task-detail-view" :key="forceUpdateKey">
    <div v-if="taskStore.isLoading">正在加载任务详情...</div>
    <div v-if="taskStore.error" class="error-message">{{ taskStore.error }}</div>

    <div v-if="taskStore.currentTask && taskStore.currentTask.id" class="task-container">
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
  </div>
</template>

<style scoped>
/* 样式保持完全不变 */
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
.status.failure {
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
