import { ThunderboltOutlined } from '@ant-design/icons'
import Button from './Button'

const NODE_LABELS = {
  input_validator: 'Input Validator',
  brief_analyst: 'Brief Analyst',
  campaign_architect: 'Campaign Architect',
  channel_expander: 'Channel Expander',
  task_assembler: 'Task Assembler',
  proposal_formatter: 'Proposal Formatter',
  approval_handler: 'Approval Handler',
  revision_parser: 'Revision Parser',
  metrics_fetcher: 'Metrics Fetcher',
  insights_synthesizer: 'Insights Synthesizer',
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

function statusClass(status) {
  if (status === 'complete') return 'success'
  if (status === 'error') return 'error'
  if (status === 'running') return 'running'
  if (status === 'waiting') return 'waiting'
  return ''
}

export default function LiveStreamView({ events = [], streamText = '', onClear }) {
  return (
    <aside className="chat-stream">
      <div className="stream-header">
        <div className="stream-title">
          <ThunderboltOutlined style={{ marginRight: 6 }} />
          Live Agent Stream
        </div>
        <Button variant="ghost" size="sm" onClick={onClear}>
          Clear
        </Button>
      </div>

      <div className="stream-body">
        {streamText && (
          <div className="stream-text-box">
            <div className="stream-text-label">Assistant Output</div>
            <pre className="stream-text-content">{streamText}</pre>
          </div>
        )}

        {events.length === 0 && !streamText && (
          <div className="stream-empty">
            <div className="stream-empty-icon">
              <ThunderboltOutlined />
            </div>
            <div>Agent events will appear here as the pipeline runs</div>
          </div>
        )}

        {events.map((ev, idx) => (
          <div key={idx} className={`stream-event ${statusClass(ev.status)}`}>
            <div className="stream-event-header">
              <span className="stream-event-node">
                {NODE_LABELS[ev.node] || ev.node}
              </span>
              <span className={`stream-event-status ${ev.status}`}>
                {ev.status}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span className="stream-event-domain">{ev.domain}</span>
              <span className="stream-event-time">{formatTime(ev.timestamp)}</span>
            </div>
            {ev.error_message && (
              <div style={{ fontSize: 11, color: '#e74c3c', marginTop: 3 }}>
                {ev.error_message}
              </div>
            )}
          </div>
        ))}
      </div>
    </aside>
  )
}
