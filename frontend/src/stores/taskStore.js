import { defineStore } from 'pinia'
import api from '@/services/api'

export const useTaskStore = defineStore('task', {
  state: () => ({
    currentTask: {},
    isLoading: false,
    error: null,
    isConnected: false,
    socket: null,
  }),
  actions: {
    async fetchTask(taskId) {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.getTask(taskId)
        this.$patch({ currentTask: response.data })
      } catch (err) {
        console.error('获取任务详情失败:', err)
        this.error = '无法加载任务详情。'
      } finally {
        this.isLoading = false
      }
    },
    connectWebSocket() {
      if (this.isConnected) return
      this.socket = new WebSocket('ws://localhost:8000/ws/task-updates/') // 代理会自动处理
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
          if (this.currentTask && this.currentTask.id === updatedTask.id) {
            this.currentTask.status = updatedTask.status
            this.currentTask.log = updatedTask.log
            this.currentTask.latest_screenshot_url = updatedTask.latest_screenshot_url
            this.currentTask.completed_at = updatedTask.completed_at
          }
        }
      }
    },
    disconnectWebSocket() {
      if (this.socket) this.socket.close()
    },
  },
})
