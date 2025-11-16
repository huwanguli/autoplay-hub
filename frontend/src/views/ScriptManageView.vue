<script setup>
import { ref, onMounted, computed } from 'vue'
import { useScriptStore } from '@/stores/scriptStore'
import { storeToRefs } from 'pinia'

// 1. 导入 CodeMirror 组件和相关模块
import { Codemirror } from 'vue-codemirror'
import { json } from '@codemirror/lang-json'
import { oneDark } from '@codemirror/theme-one-dark'

// --- 初始化 Store ---
const scriptStore = useScriptStore()
const { scripts, isLoading, error } = storeToRefs(scriptStore)

// --- 本地状态管理 ---
const currentMode = ref('view')
const editingScript = ref(null)

const scriptContentForEdit = computed({
  get: () => {
    if (!editingScript.value) return ''
    // 如果 content 是对象，则格式化；如果是字符串，则直接返回
    if (typeof editingScript.value.content === 'object') {
      return JSON.stringify(editingScript.value.content, null, 2)
    }
    return editingScript.value.content
  },
  set: (value) => {
    if (editingScript.value) {
      // 在编辑过程中，content 始终是字符串
      editingScript.value.content = value
    }
  },
})

const fileInput = ref(null)

// 2. 配置 CodeMirror 的扩展
const extensions = [json(), oneDark]

// --- 行为函数 ---
const openCreator = () => {
  const initialContent = { version: '2.0', name: '新脚本', description: '', steps: [] }
  editingScript.value = {
    name: '',
    description: '',
    content: JSON.stringify(initialContent, null, 2), // 初始化为字符串
  }
  currentMode.value = 'edit'
}

const openEditor = (script) => {
  editingScript.value = JSON.parse(JSON.stringify(script))
  // 确保content在编辑时是一个字符串
  if (typeof editingScript.value.content !== 'string') {
    editingScript.value.content = JSON.stringify(editingScript.value.content, null, 2)
  }
  currentMode.value = 'edit'
}

const closeEditor = () => {
  editingScript.value = null
  currentMode.value = 'view'
}

const saveScript = async () => {
  if (!editingScript.value) return

  try {
    // 在保存前，进行最终的JSON解析
    const finalContent = JSON.parse(
      typeof editingScript.value.content === 'string'
        ? editingScript.value.content
        : JSON.stringify(editingScript.value.content),
    )

    const scriptToSave = {
      ...editingScript.value,
      content: finalContent,
    }

    if (scriptToSave.id) {
      await scriptStore.updateScript(scriptToSave.id, scriptToSave)
    } else {
      await scriptStore.createScript(scriptToSave)
    }
    closeEditor()
  } catch (e) {
    alert('保存失败！请检查脚本内容是否为有效的JSON格式。')
  }
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const fileContent = JSON.parse(e.target.result)
      editingScript.value.name = fileContent.name || file.name.replace('.json', '')
      editingScript.value.description = fileContent.description || ''
      // 将文件内容格式化为字符串，以适应CodeMirror
      editingScript.value.content = JSON.stringify(fileContent, null, 2)
      alert('脚本文件加载成功！')
    } catch (err) {
      alert('加载失败！文件不是有效的JSON格式。')
    }
  }
  reader.readAsText(file)
  event.target.value = ''
}

const triggerFileUpload = () => {
  fileInput.value.click()
}

const handleDeleteScript = async (script) => {
  if (confirm(`确定要删除脚本 "${script.name}" 吗？此操作无法撤销。`)) {
    await scriptStore.deleteScript(script.id)
  }
}

// --- 生命周期钩子 ---
onMounted(() => {
  scriptStore.fetchScripts()
})
</script>

<template>
  <div class="script-manager">
    <!-- ==================== 列表视图 ==================== -->
    <div v-if="currentMode === 'view'">
      <div class="header">
        <h2>脚本列表</h2>
        <button @click="openCreator" class="btn-primary">创建新脚本</button>
      </div>

      <div v-if="isLoading">正在加载...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <table v-else-if="scripts.length > 0">
        <thead>
          <tr>
            <th>ID</th>
            <th>名称</th>
            <th>描述</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="script in scripts" :key="script.id">
            <td>{{ script.id }}</td>
            <td>{{ script.name }}</td>
            <td>{{ script.description }}</td>
            <td class="actions">
              <button @click="openEditor(script)" class="btn-secondary">编辑</button>
              <button @click="handleDeleteScript(script)" class="btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else>暂无脚本，请创建一个。</div>
    </div>

    <!-- ==================== 编辑器视图 ==================== -->
    <div v-if="currentMode === 'edit'" class="editor-view">
      <div class="header">
        <h2>{{ editingScript.id ? '编辑脚本' : '创建新脚本' }}</h2>
      </div>
      <form @submit.prevent="saveScript" class="script-form">
        <div class="form-group">
          <label for="name">脚本名称</label>
          <input id="name" v-model="editingScript.name" required />
        </div>
        <div class="form-group">
          <label for="description">脚本描述</label>
          <textarea id="description" v-model="editingScript.description" rows="3"></textarea>
        </div>

        <div class="form-group">
          <div class="content-header">
            <label for="content">脚本内容 (JSON格式)</label>
            <button type="button" @click="triggerFileUpload" class="btn-secondary btn-small">
              从文件加载
            </button>
          </div>
          <input
            type="file"
            ref="fileInput"
            @change="handleFileUpload"
            accept=".json"
            style="display: none"
          />

          <!-- 3. 用 Codemirror 组件替换掉 textarea -->
          <codemirror
            v-model="scriptContentForEdit"
            placeholder="在此输入或加载JSON脚本..."
            :style="{ height: '400px' }"
            :autofocus="true"
            :indent-with-tab="true"
            :tab-size="2"
            :extensions="extensions"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-primary">保存</button>
          <button type="button" @click="closeEditor" class="btn-secondary">取消</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* 通用样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-danger {
  background-color: #dc3545;
  color: white;
}
button {
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}
button:hover {
  opacity: 0.9;
}
.error {
  color: #dc3545;
}

/* 表格样式 */
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
.actions button {
  margin-right: 0.5rem;
  padding: 0.4rem 0.8rem;
}

/* 表单样式 */
.script-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group label {
  margin-bottom: 0.5rem;
  font-weight: bold;
}
input,
textarea {
  padding: 0.7rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
}
.form-actions {
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
}

/* CodeMirror 和文件上传相关样式 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.content-header label {
  margin-bottom: 0;
}
.btn-small {
  padding: 0.3rem 0.8rem;
  font-size: 0.85rem;
}
.script-form :deep(.cm-editor) {
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
