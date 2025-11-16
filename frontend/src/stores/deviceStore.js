import { defineStore } from 'pinia'
import api from '@/services/api' // 我们稍后会更新api.js

export const useDeviceStore = defineStore('devices', {
  // state: 定义这个模块需要“记住”的数据
  state: () => ({
    devices: [], // ★ 用于存储从后端获取的设备列表
    selectedDeviceUri: null, // ★ 用于存储用户当前选择的设备URI
    isLoading: false, // 一个标志，告诉UI我们是否正在加载设备列表
    error: null, // 如果加载失败，这里会存储错误信息
  }),

  // actions: 定义可以对数据进行哪些“操作”
  actions: {
    // 操作1: 从后端获取设备列表
    async fetchDevices() {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.getDevices() // 调用API
        this.devices = response.data // 将获取到的设备列表存入 state

        // ★ 一个友好的交互：如果之前没有选择过设备，并且列表不为空，就自动选择第一个
        if (!this.selectedDeviceUri && this.devices.length > 0) {
          this.selectedDeviceUri = this.devices[0].uri
        }
      } catch (err) {
        this.error = '无法加载设备列表。请检查后端服务和ADB连接。'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    // 操作2: 允许用户手动选择一个设备
    selectDevice(deviceUri) {
      this.selectedDeviceUri = deviceUri
    },
  },
})
