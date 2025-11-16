import { ref } from 'vue'

export function useWebSocket() {
  const ws = ref(null)
  const isConnected = ref(false)

  // 根据当前协议 (http/https) 和主机，构造 WebSocket 的 URL
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsURL = `${protocol}//${window.location.host}/ws/task_updates/`

  ws.value = new WebSocket(wsURL)

  ws.value.onopen = () => {
    isConnected.value = true
    console.log('WebSocket连接已建立')
  }

  ws.value.onclose = () => {
    isConnected.value = false
    console.log('WebSocket连接已断开')
  }

  ws.value.onerror = (error) => {
    console.error('WebSocket错误:', error)
  }

  // 核心：设置消息处理器
  const onMessage = (callback) => {
    if (ws.value) {
      ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data)
        // 我们假设后端发送的数据总是有一个 'message' 字段
        callback(data.message)
      }
    }
  }

  const close = () => {
    if (ws.value) {
      ws.value.close()
    }
  }

  return { onMessage, close, isConnected }
}
