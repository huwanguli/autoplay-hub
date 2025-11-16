<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useTaskHistoryStore } from '@/stores/taskHistoryStore'
import { storeToRefs } from 'pinia'

// --- 初始化 Store ---
const taskHistoryStore = useTaskHistoryStore()
const { tasks, isLoading, error } = storeToRefs(taskHistoryStore)

// --- 行为函数 ---
// 一个辅助函数，用于格式化日期，使其更友好
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

// --- 生命周期钩子 ---
onMounted(() => {
  taskHistoryStore.fetchTasks()
})
</script>

<template>
  <div class="task-history-manager">
    <div class="header">
      <h2>任务历史记录</h2>
    </div>

    <div v-if="isLoading">正在加载...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <table v-else-if="tasks.length > 0">
      <thead>
        <tr>
          <th>ID</th>
          <th>脚本名称</th>
          <th>状态</th>
          <th>创建时间</th>
          <th>完成时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="task in tasks" :key="task.id">
          <td>#{{ task.id }}</td>
          <td>{{ task.script_name }}</td>
          <td>
            <span :class="`status-${task.status.toLowerCase()}`">{{ task.status }}</span>
          </td>
          <td>{{ formatDate(task.created_at) }}</td>
          <td>{{ formatDate(task.completed_at) }}</td>
          <td class="actions">
            <!-- 关键：每一行都有一个链接到详情页 -->
            <RouterLink
              :to="{ name: 'task-detail', params: { id: task.id } }"
              class="btn-primary btn-small"
            >
              查看详情
            </RouterLink>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else>还没有任何任务记录。</div>
  </div>
</template>

<style scoped>
/* 样式与ScriptManageView非常相似，保持风格统一 */
.header {
  margin-bottom: 1.5rem;
}
.btn-primary {
  background-color: #007bff;
  color: white;
  text-decoration: none;
  display: inline-block;
}
.btn-small {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
  border-radius: 4px;
}
.error {
  color: #dc3545;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  border: 1px solid #ddd;
  padding: 0.8rem;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}

/* 任务状态的颜色样式 */
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
</style>
