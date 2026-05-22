export default function HistoryList({ items = [] }) {
  return (
    <div className="history-section">
      <div className="history-label">History</div>
      {items.length === 0 ? (
        <div className="history-empty">No campaigns yet</div>
      ) : (
        items.map((item) => (
          <div key={item.id} className="history-item">
            <div className="history-item-name">{item.name}</div>
            <div className="history-item-meta">{item.meta}</div>
          </div>
        ))
      )}
    </div>
  )
}
