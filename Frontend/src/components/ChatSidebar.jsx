import TabNav from './TabNav'
import NewChatButton from './NewChatButton'
import SearchInput from './SearchInput'
import HistoryList from './HistoryList'
import { useState } from 'react'

export default function ChatSidebar({ activeView, onViewChange, onNewChat, history = [] }) {
  const [search, setSearch] = useState('')

  const filtered = history.filter((h) =>
    h.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="brand">MARA</span>
        <NewChatButton onClick={onNewChat} disabledStatus={true}/>
      </div>

      <TabNav activeView={activeView} onChange={onViewChange} />

      <SearchInput value={search} onChange={setSearch} />

      <HistoryList items={filtered} />
    </aside>
  )
}
