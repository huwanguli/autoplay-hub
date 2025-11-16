import axios from 'axios'

// 创建一个axios实例，我们可以进行统一的配置
const apiClient = axios.create({
  baseURL: '/api', // Vite会自动代理到 http://127.0.0.1:8000/api
  headers: {
    'Content-Type': 'application/json',
  },
})

// ★ 这里定义了我们所有与后端交互的请求
export default {
  // 获取设备列表
  getDevices() {
    return apiClient.get('/devices/')
  },

  // 获取脚本列表
  getScripts() {
    return apiClient.get('/scripts/')
  },

  // 运行脚本
  runScript(scriptId, deviceUri) {
    // 发送一个POST请求，并在请求体(body)中包含device_uri
    return apiClient.post(`/scripts/${scriptId}/run/`, {
      device_uri: deviceUri,
    })
  },

  // 获取单个任务的详情 (为我们下一步的详情页做准备)
  getTask(taskId) {
    return apiClient.get(`/tasks/${taskId}/`)
  },

  triggerManualScreenshot(taskId) {
    return apiClient.post(`/tasks/${taskId}/screenshot/`)
  },
}
