import { useState, useCallback } from 'react'
import ChatSidebar from './ChatSidebar'
import ChatWindow from './ChatWindow'

export default function ChatLayout() {
  const [activeView, setActiveView] = useState('Chat')
  const [resetKey, setResetKey] = useState(0)
  const [history, setHistory] = useState([])

  const handleNewChat = useCallback(() => {
    setResetKey((k) => k + 1)
    setActiveView('Chat')
  }, [])

  const handleCampaignStarted = useCallback(({ campaign_id, session_id, name }) => {
    setHistory((prev) => [
      { id: campaign_id, name: name || 'Campaign', meta: new Date().toLocaleTimeString() },
      ...prev,
    ])
  }, [])

  const externalSplit = activeView === 'Live Stream'

  return (
    <div className="chat-root">
      <ChatSidebar
        activeView={activeView}
        onViewChange={setActiveView}
        onNewChat={handleNewChat}
        history={history}
      />
      <ChatWindow
        activeView={activeView}
        resetKey={resetKey}
        externalSplit={externalSplit}
        onCampaignStarted={handleCampaignStarted}
      />
    </div>
  )
}
