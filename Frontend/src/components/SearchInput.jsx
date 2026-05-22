import { SearchOutlined } from '@ant-design/icons'

export default function SearchInput({ value, onChange, placeholder = 'Search campaigns...' }) {
  return (
    <div className="search">
      <SearchOutlined className="search-icon" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  )
}
