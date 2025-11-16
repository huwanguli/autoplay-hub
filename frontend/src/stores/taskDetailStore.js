import { defineStore } from 'pinia'
import api from '@/services/api'
import { useWebSocket } from '@/services/websocket' // 我们将创建一个新的websocket服务

export const useTaskDetailStore = defineStore('taskDetail', {
  state: () => ({
    task: null, // 存储当前正在查看的任务对象
    isLoading: false,
    error: null,
    ws: null, // 用于存放WebSocket连接实例
  }),
  actions: {
    // 从后端获取指定ID的任务的初始数据
    async fetchTask(taskId) {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.getTask(taskId)
        this.task = response.data
      } catch (err) {
        this.error = '无法加载任务详情。'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    // 连接到WebSocket以接收实时更新
    connectWebSocket() {
      // 确保任务数据已加载
      if (!this.task || !this.task.id) return
      this.ws = useWebSocket()

      // 告诉WebSocket服务当收到消息时该做什么
      this.ws.onMessage((data) => {
        // 我们只关心与当前正在查看的任务ID相匹配的更新
        const updatedTask = data.message

        // 确保收到的消息是我们需要的任务更新消息
        if (updatedTask && updatedTask.id === this.task.id) {
          console.log('收到任务更新:', updatedTask)

          // 直接用收到的新数据替换旧的任务数据，界面就会自动更新
          this.task = updatedTask
        }
      })
    },

    async triggerScreenshot() {
      if (!this.task) return
      try {
        await api.triggerManualScreenshot(this.task.id)
        // 我们不需要在这里做什么，因为后端的WebSocket会自动发送更新
        // 可以在这里加一个用户提示，比如一个短暂的 "指令已发送" Toast
        console.log('手动截图指令已发送')
      } catch (err) {
        alert(`截图失败: ${err.response?.data?.error || err.message}`)
        console.error(err)
      }
    },

    // 断开WebSocket连接（当用户离开页面时调用）
    disconnectWebSocket() {
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
    },

    // 清理任务数据（当用户离开页面时调用，为下次进入做准备）
    clearTask() {
      this.task = null
    },
  },
})
