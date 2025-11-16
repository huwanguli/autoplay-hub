<script setup>
import { onMounted } from 'vue'
import { useDeviceStore } from '@/stores/deviceStore'
import { useScriptStore } from '@/stores/scriptStore'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
// --- 1. 获取“脑袋” ---
const deviceStore = useDeviceStore()
const scriptStore = useScriptStore()
const router = useRouter()

// --- 2. 状态链接 ---
// 使用 storeToRefs 从“大脑”中取出我们需要在界面上显示的数据
// 这样做的好处是，当 store 中的数据变化时，我们的界面会自动更新
const {
  devices,
  selectedDeviceUri,
  isLoading: isDevicesLoading,
  error: deviceError,
} = storeToRefs(deviceStore)
const { scripts, isLoading: isScriptsLoading, error: scriptError } = storeToRefs(scriptStore)

// --- 3. 定义行为 ---
// 定义一个函数，当用户点击“运行”按钮时执行
const handleRunScript = async (scriptId) => {
  // 调用 scriptStore 中的 action 来运行脚本
  // 它需要两个参数：脚本ID 和 当前选中的设备URI
  const newTask = await scriptStore.runScript(scriptId, selectedDeviceUri.value)

  // 如果成功创建了任务，就跳转到任务详情页
  if (newTask) {
    router.push({ name: 'task-detail', params: { id: newTask.id } })
  }
}

// 定义一个函数，当用户在下拉菜单中选择新设备时执行
const handleDeviceSelection = (event) => {
  // 调用 deviceStore 中的 action 来更新当前选择的设备
  deviceStore.selectDevice(event.target.value)
}

// --- 4. 生命周期钩子 ---
// onMounted 会在组件第一次被加载到屏幕上后自动执行
onMounted(() => {
  // 指示 stores 去后端获取最新的设备列表和脚本列表
  deviceStore.fetchDevices()
  scriptStore.fetchScripts()
})
</script>

<template>
  <div class="hub-container">
    <!-- Section 1: 设备选择 -->
    <section class="device-selector">
      <h2>1. 选择目标设备</h2>
      <div v-if="isDevicesLoading">正在加载设备列表...</div>
      <div v-else-if="deviceError" class="error">{{ deviceError }}</div>
      <!-- 当设备列表加载完毕后，显示下拉菜单 -->
      <select
        v-else-if="devices.length > 0"
        :value="selectedDeviceUri"
        @change="handleDeviceSelection"
      >
        <option v-for="device in devices" :key="device.uri" :value="device.uri">
          {{ device.model }} ({{ device.serial }})
        </option>
      </select>
      <div v-else>未发现任何可用设备。</div>
    </section>

    <!-- Section 2: 脚本列表 -->
    <section class="script-list">
      <h2>2. 选择要运行的脚本</h2>
      <div v-if="isScriptsLoading">正在加载脚本列表...</div>
      <div v-else-if="scriptError" class="error">{{ scriptError }}</div>
      <!-- 当脚本列表加载完毕后，显示表格 -->
      <table v-else-if="scripts.length > 0">
        <thead>
          <tr>
            <th>脚本名称</th>
            <th>描述</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="script in scripts" :key="script.id">
            <td>{{ script.name }}</td>
            <td>{{ script.description }}</td>
            <td>
              <!-- 运行按钮。点击时调用 handleRunScript 函数 -->
              <button @click="handleRunScript(script.id)" :disabled="!selectedDeviceUri">
                运行
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else>没有找到任何脚本。</div>
    </section>
  </div>
</template>

<style scoped>
.hub-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

section {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

select {
  width: 100%;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ddd;
  padding: 0.8rem;
  text-align: left;
}

th {
  background-color: #f2f2f2;
}

button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #0056b3;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error {
  color: #dc3545;
}
</style>
