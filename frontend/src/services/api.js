import axios from 'axios'

// 创建一个Axios实例
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

//console.log('API Client Base URL is:', apiClient.defaults.baseURL)

// 导出一个包含了所有API方法的对象
export default {
  /**
   * 获取脚本列表
   */
  getScripts() {
    // 这里的 '/scripts/' 会被自动拼接到 baseURL 后面，
    // 形成完整的请求URL: http://127.0.0.1:8000/api/scripts/
    //console.log('Calling getScripts()...')
    return apiClient.get('/scripts/')
  },

  runScript(scriptId) {
    return apiClient.post(`/scripts/${scriptId}/run/`)
  },

  getTask(taskId) {
    return apiClient.get(`/tasks/${taskId}/`)
  },
}
