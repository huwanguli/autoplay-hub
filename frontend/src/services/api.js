import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// ★ 新增：使用拦截器在每次请求前，检查并添加 Authorization 头
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

const api = {
  // --- 认证相关 ---
  login(credentials) {
    // dj-rest-auth默认返回的user信息比较少，我们可以在这里做扩展
    // 但为了简化，我们先直接用
    return apiClient.post('/auth/login/', credentials)
  },
  register(credentials) {
    return apiClient.post('/auth/registration/', credentials)
  },
  setAuthHeader(token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },
  clearAuthHeader() {
    delete apiClient.defaults.headers.common['Authorization']
  },

  // --- 脚本相关 (Script) ---
  getScripts() {
    return apiClient.get('/scripts/')
  },
  getScript(id) {
    return apiClient.get(`/scripts/${id}/`)
  },
  createScript(script) {
    return apiClient.post('/scripts/', script)
  },
  updateScript(id, script) {
    return apiClient.put(`/scripts/${id}/`, script)
  },
  deleteScript(id) {
    return apiClient.delete(`/scripts/${id}/`)
  },
  runScript(id, deviceUri) {
    return apiClient.post(`/scripts/${id}/run/`, { device_uri: deviceUri })
  },

  // --- 任务相关 (Task) ---
  getTasks() {
    return apiClient.get('/tasks/')
  },
  getTask(id) {
    return apiClient.get(`/tasks/${id}/`)
  },
  cancelTask(taskId) {
    return apiClient.post(`/tasks/${taskId}/cancel/`)
  },
  manualScreenshot(taskId) {
    return apiClient.post(`/tasks/${taskId}/screenshot/`)
  },

  // --- 设备相关 (Device) ---
  getDevices() {
    return apiClient.get('/devices/')
  },
}

export default api
