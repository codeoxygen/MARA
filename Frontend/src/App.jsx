import './index.css'
import './chat.css'
import ChatLayout from './components/ChatLayout'
import { ToastProvider } from './components/Toast'

export default function App() {
  return (
    <ToastProvider>
      <ChatLayout />
    </ToastProvider>
  )
}
