function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function MessageBubble({ message }) {
  const { role, content, timestamp, isTyping } = message

  if (isTyping) {
    return (
      <div className="typing-indicator">
        <div className="typing-dot" />
        <div className="typing-dot" />
        <div className="typing-dot" />
      </div>
    )
  }

  const isUser = role === 'user'
  const isSystem = role === 'system'

  return (
    <div className={`message-bubble ${role}`}>
      {!isSystem && (
        <div className="message-meta">
          <span className={`message-sender ${role}`}>
            {isUser ? 'You' : 'MARA'}
          </span>
          {timestamp && <span className="message-time">{formatTime(timestamp)}</span>}
        </div>
      )}
      <div className="message-content">{content}</div>
    </div>
  )
}
