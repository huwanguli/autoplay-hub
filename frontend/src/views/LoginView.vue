<template>
  <div class="auth-container">
    <div class="auth-form">
      <h2>登录您的账户</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" v-model="username" id="username" required />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" v-model="password" id="password" required />
        </div>
        <div v-if="authStore.authError" class="error-message">
          {{ authStore.authError }}
        </div>
        <button type="submit" :disabled="authStore.authLoading">
          {{ authStore.authLoading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p>还没有账户？ <router-link to="/register">立即注册</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const username = ref('')
const password = ref('')
const authStore = useAuthStore()

const handleLogin = () => {
  authStore.login({ username: username.value, password: password.value })
}
</script>

<style scoped>
/* (可以添加一些美化样式) */
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}
.auth-form {
  width: 350px;
  padding: 2rem;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.form-group {
  margin-bottom: 1rem;
}
.error-message {
  color: red;
  margin-bottom: 1rem;
}
</style>
