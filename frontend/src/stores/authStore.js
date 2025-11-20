import { defineStore } from 'pinia'
import api from '@/services/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', {
  // 1. 定义状态：从localStorage初始化，这样刷新页面后登录状态不会丢失
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')),
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    // 用于在登录/注册时显示加载状态或错误信息
    authError: null,
    authLoading: false,
  }),

  // 2. 定义Getters：方便地判断用户是否登录
  getters: {
    isAuthenticated: (state) => !!state.accessToken && !!state.user,
    // (可以添加其他getters，如isAdmin等)
  },

  // 3. 定义Actions：所有与认证相关的操作
  actions: {
    async login(credentials) {
      this.authLoading = true
      this.authError = null
      try {
        const response = await api.login(credentials)

        // 从响应中获取tokens和用户信息
        const { access, refresh, user } = response.data

        // 更新 Pinia state
        this.accessToken = access
        this.refreshToken = refresh
        this.user = user

        // 将数据存入 localStorage 以实现持久化登录
        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('accessToken', access)
        localStorage.setItem('refreshToken', refresh)

        // ★ 关键: 更新axios的请求头，让后续所有请求都带上token
        api.setAuthHeader(access)

        // 登录成功后跳转到主页
        await router.push('/')
      } catch (error) {
        this.authError = '用户名或密码错误。'
        console.error('登录失败:', error)
      } finally {
        this.authLoading = false
      }
    },

    async register(credentials) {
      this.authLoading = true
      this.authError = null
      try {
        await api.register(credentials)
        // 注册成功后，自动使用相同信息登录
        await this.login({ username: credentials.username, password: credentials.password1 })
      } catch (error) {
        // 处理注册失败的各种情况（例如用户名已存在）
        this.authError = error.response?.data?.username?.[0] || '注册失败，请检查输入。'
        console.error('注册失败:', error)
      } finally {
        this.authLoading = false
      }
    },

    logout() {
      // 清空 Pinia state
      this.user = null
      this.accessToken = null
      this.refreshToken = null

      // 清空 localStorage
      localStorage.removeItem('user')
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')

      // ★ 关键: 移除axios的请求头
      api.clearAuthHeader()

      // 登出后跳转到登录页面
      router.push('/login')
    },

    // (未来可以添加刷新token的逻辑)
  },
})
