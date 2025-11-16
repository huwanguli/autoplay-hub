import { defineStore } from 'pinia'
import { useRouter } from 'vue-router' // 引入路由，方便运行后跳转
import api from '@/services/api'

export const useScriptStore = defineStore('scripts', {
  state: () => ({
    scripts: [], // 存储脚本列表
    isLoading: false, // 加载状态
    error: null, // 错误信息
  }),

  actions: {
    // 从后端获取所有脚本
    async fetchScripts() {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.getScripts()
        this.scripts = response.data
      } catch (err) {
        this.error = '无法加载脚本列表。'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    // ★ 运行一个脚本（这是核心逻辑！）
    async runScript(scriptId, deviceUri) {
      // 检查是否传入了deviceUri，如果没有则报错，增加程序的健壮性
      if (!deviceUri) {
        alert('错误：必须先选择一个设备！')
        return // 中止运行
      }

      try {
        // 调用后端API，并把 scriptId 和 deviceUri 一起发过去
        const response = await api.runScript(scriptId, deviceUri)
        const newTask = response.data // 后端会返回新创建的任务信息

        // ★ 运行成功后，自动跳转到该任务的详情页
        // 这是Vue 3的路由用法，我们在组件中会更容易使用，这里先注释掉
        // const router = useRouter(); // 在store中直接使用useRouter()不被推荐
        // router.push({ name: 'task-detail', params: { id: newTask.id } });

        // 我们返回新任务，让调用它的组件来负责跳转
        return newTask
      } catch (err) {
        alert(`运行脚本失败: ${err.response?.data?.error || err.message}`)
        console.error(err)
      }
    },
  },
})
