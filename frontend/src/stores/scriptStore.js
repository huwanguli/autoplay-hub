import { defineStore } from 'pinia'
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
        return newTask
      } catch (err) {
        alert(`运行脚本失败: ${err.response?.data?.error || err.message}`)
        console.error(err)
      }
    },

    async createScript(scriptData) {
      try {
        await api.createScript(scriptData)
        // ★ 创建成功后，刷新列表以显示新脚本
        await this.fetchScripts()
      } catch (err) {
        console.error('创建脚本失败:', err)
        // 抛出错误，让UI可以捕获并显示给用户
        throw err
      }
    },

    async updateScript(scriptId, scriptData) {
      try {
        await api.updateScript(scriptId, scriptData)
        await this.fetchScripts()
      } catch (err) {
        console.error('更新脚本失败:', err)
        throw err
      }
    },

    async deleteScript(scriptId) {
      try {
        await api.deleteScript(scriptId)
        await this.fetchScripts()
      } catch (err) {
        console.error('删除脚本失败:', err)
        throw err
      }
    },
  },
})
