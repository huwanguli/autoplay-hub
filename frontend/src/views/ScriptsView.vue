<script setup>
import { onMounted } from 'vue'
import { useScriptStore } from '@/stores/scriptStore'
import { storeToRefs } from 'pinia'

const scriptStore = useScriptStore()
const { scripts, isLoading, error } = storeToRefs(scriptStore)

// 新增一个函数，用于处理点击事件
function handleRunScript(scriptId) {
  console.log(`准备运行脚本 #${scriptId}`)
  scriptStore.runScript(scriptId)
}

onMounted(() => {
  scriptStore.fetchScripts()
})
</script>

<template>
  <div class="scripts-view">
    <h1>自动化脚本列表</h1>

    <!-- ... 加载和错误状态的模板保持不变 ... -->
    <div v-if="isLoading">正在加载或执行操作...</div>
    <div v-if="error" class="error-message">...</div>

    <ul v-if="!isLoading && scripts.length > 0" class="script-list">
      <li v-for="script in scripts" :key="script.id" class="script-item">
        <div class="script-info">
          <div class="script-header">
            <strong>{{ script.name }}</strong>
            <span>(ID: {{ script.id }})</span>
          </div>
          <p class="script-description">{{ script.description || '暂无描述' }}</p>
        </div>
        <!-- 这是我们新增的运行按钮 -->
        <button @click="handleRunScript(script.id)" class="run-button">运行</button>
      </li>
    </ul>

    <!-- ... 没有数据的模板保持不变 ... -->
    <div v-if="!isLoading && !error && scripts.length === 0">...</div>
  </div>
</template>

<style scoped>
/* 更新样式以适应按钮 */
.script-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9f9f9;
  border: 1px solid #eee;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  border-radius: 8px;
  transition: box-shadow 0.2s;
}
.script-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}
.script-info {
  flex-grow: 1;
}
.run-button {
  background-color: hsla(160, 100%, 37%, 1);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  margin-left: 2rem;
  transition: background-color 0.2s;
}
.run-button:hover {
  background-color: hsla(160, 100%, 30%, 1);
}
/* 其他样式保持不变 */
.scripts-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: sans-serif;
}
.loading,
.no-data {
  text-align: center;
  color: #666;
  padding: 2rem;
}
.error-message {
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #c62828;
  border-radius: 5px;
  padding: 1rem;
}
.script-list {
  list-style-type: none;
  padding: 0;
}
.script-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}
.script-header span {
  font-size: 0.9rem;
  color: #888;
}
.script-description {
  color: #555;
  margin: 0;
}
</style>
