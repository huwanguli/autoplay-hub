import { defineStore } from 'pinia'
import api from '@/services/api'
import router from '@/router'

export const useScriptStore = defineStore('script', {
  state: () => ({
    scripts: [],
    isLoading: false,
    error: null,
  }),

  // 2. 定义Actions：包含可以被调用的方法，用于改变State
  actions: {
    /**
     * 从API获取脚本列表并更新state
     */
    async fetchScripts() {
      this.isLoading = true // 开始加载，设置isLoading为true
      this.error = null // 清除之前的错误

      try {
        // 调用API服务中的getScripts方法
        const response = await api.getScripts()
        // 成功后，用返回的数据更新scripts数组
        this.scripts = response.data
      } catch (err) {
        // 如果发生错误
        console.error('获取脚本列表失败:', err)
        this.error = '无法加载脚本列表。请检查后端服务是否正在运行以及CORS配置是否正确。'
      } finally {
        // 无论成功还是失败，最后都结束加载状态
        this.isLoading = false
      }
    },

    async runScript(scriptId) {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.runScript(scriptId)
        const new_task = response.data
        console.log('新任务已创建:', new_task)

        // **成功后，跳转到新的任务详情页**
        // 我们稍后会创建这个页面
        router.push({ name: 'task-detail', params: { id: new_task.id } })
      } catch (err) {
        console.error(`运行脚本 #${scriptId} 失败:`, err)
        this.error = `无法运行脚本。`
      } finally {
        this.isLoading = false
      }
    },
  },
})
