import { defineStore } from 'pinia'
import api from '@/services/api'

export const useTaskStore = defineStore('task', {
  state: () => ({
    // ★ 关键改动 1：初始状态设为 null，让组件的 v-if 判断更清晰
    currentTask: null,
    isLoading: false,
    error: null,
    isConnected: false,
    socket: null,
  }),
  actions: {
    async fetchTask(taskId) {
      this.isLoading = true
      this.error = null
      this.currentTask = null // ★ 在获取前，先清空旧数据
      try {
        const response = await api.getTask(taskId)
        this.currentTask = response.data // 直接赋值
      } catch (err) {
        console.error('获取任务详情失败:', err)
        this.error = '无法加载任务详情。'
      } finally {
        this.isLoading = false
      }
    },
    connectWebSocket() {
      if (this.isConnected) return
      // ★ 使用相对路径，让 Vite 代理来处理
      this.socket = new WebSocket(`ws://${window.location.host}/ws/task-updates/`)
      this.socket.onopen = () => {
        this.isConnected = true
      }
      this.socket.onclose = () => {
        this.isConnected = false
      }
      this.socket.onerror = (error) => {
        console.error('WebSocket Error:', error)
      }

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'task.update') {
          const updatedTask = data.message

          // ★ 关键改动 2：采用“先清空再赋值”的方式，强制Vue识别到这是一个“全新”的对象
          if (this.currentTask && this.currentTask.id === updatedTask.id) {
            this.currentTask = null
            // 使用 nextTick 确保DOM更新后再赋值，但这在store中不是最佳实践
            // 我们直接用最简单的方式：
            this.currentTask = updatedTask
          }
        }
      }
    },
    disconnectWebSocket() {
      if (this.socket) this.socket.close()
    },
  },
})
