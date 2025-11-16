import { defineStore } from 'pinia'
import api from '@/services/api'

export const useTaskHistoryStore = defineStore('taskHistory', {
  state: () => ({
    tasks: [],
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchTasks() {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.getTasks()
        // 假设后端已禁用分页，直接将返回的数组赋值
        this.tasks = response.data
      } catch (err) {
        this.error = '无法加载任务历史。'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },
  },
})
