import { Input } from 'antd'
import { SendOutlined } from '@ant-design/icons'
import { useRef } from 'react'

export default function ChatInput({ onSend, disabled = false, placeholder = 'Describe your campaign brief...' }) {
  const inputRef = useRef(null)

  function handleSend() {
    const val = inputRef.current?.input?.value?.trim()
    if (!val || disabled) return
    onSend(val)
    if (inputRef.current?.input) {
      inputRef.current.input.value = ''
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-input-area">
      <Input
        ref={inputRef}
        size="large"
        placeholder={placeholder}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        suffix={
          <SendOutlined
            style={{ color: disabled ? '#444' : '#00bcd4', cursor: disabled ? 'not-allowed' : 'pointer', fontSize: 16 }}
            onClick={handleSend}
          />
        }
      />
    </div>
  )
}
