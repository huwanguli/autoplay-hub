import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export default {
  /**
   * 获取脚本列表
   */
  getScripts() {
    return apiClient.get('/scripts/')
  },

  runScript(scriptId) {
    return apiClient.post(`/scripts/${scriptId}/run/`)
  },

  getTask(taskId) {
    return apiClient.get(`/tasks/${taskId}/`)
  },
}
