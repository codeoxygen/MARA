import { createContext, useContext, useState, useCallback, useRef } from 'react'
import { CheckCircleOutlined, CloseCircleOutlined, InfoCircleOutlined, WarningOutlined, CloseOutlined } from '@ant-design/icons'

const ToastContext = createContext(null)

const ICONS = {
  success: <CheckCircleOutlined />,
  error: <CloseCircleOutlined />,
  warning: <WarningOutlined />,
  info: <InfoCircleOutlined />,
}

const DURATION = 4000

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])
  const timerRefs = useRef({})

  const dismiss = useCallback((id) => {
    clearTimeout(timerRefs.current[id])
    delete timerRefs.current[id]
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = useCallback((message, type = 'info', duration = DURATION) => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, message, type }])
    if (duration > 0) {
      timerRefs.current[id] = setTimeout(() => dismiss(id), duration)
    }
    return id
  }, [dismiss])

  const api = {
    success: (msg, dur) => toast(msg, 'success', dur),
    error: (msg, dur) => toast(msg, 'error', dur),
    warning: (msg, dur) => toast(msg, 'warning', dur),
    info: (msg, dur) => toast(msg, 'info', dur),
    dismiss,
  }

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="toast-stack">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast--${t.type}`}>
            <span className="toast-icon">{ICONS[t.type]}</span>
            <span className="toast-message">{t.message}</span>
            <button className="toast-close" onClick={() => dismiss(t.id)} aria-label="Dismiss">
              <CloseOutlined />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside ToastProvider')
  return ctx
}
