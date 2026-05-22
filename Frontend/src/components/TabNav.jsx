import { MessageOutlined, ThunderboltOutlined } from '@ant-design/icons'

const TABS = [
  { id: 'Chat', label: 'Chat', Icon: MessageOutlined }
]

export default function TabNav({ activeView, onChange }) {
  return (
    <nav className="tab-nav">
      {TABS.map(({ id, label, Icon }) => (
        <button
          key={id}
          className={`tab-nav-item ${activeView === id ? 'active' : ''}`}
          onClick={() => onChange(id)}
        >
          <Icon className="tab-icon" />
          {label}
        </button>
      ))}
    </nav>
  )
}
