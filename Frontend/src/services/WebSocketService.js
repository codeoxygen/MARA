class WebSocketService {
  constructor() {
    this.ws = null
    this.sessionId = null
    this.onMessage = null
    this.onStatusChange = null
    this.reconnectTimer = null
  }

  connect(sessionId, { onMessage, onStatusChange }) {
    this.sessionId = sessionId
    this.onMessage = onMessage
    this.onStatusChange = onStatusChange

    this._open()
  }

  _open() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/${this.sessionId}`

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this.onStatusChange?.('connected')
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.onMessage?.(data)
      } catch {
        // plain string payload
        this.onMessage?.({ type: 'text', text: event.data })
      }
    }

    this.ws.onclose = () => {
      this.onStatusChange?.('disconnected')
    }

    this.ws.onerror = () => {
      this.onStatusChange?.('error')
    }
  }

  disconnect() {
    clearTimeout(this.reconnectTimer)
    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }
    this.sessionId = null
  }

  isConnected() {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export default new WebSocketService()
