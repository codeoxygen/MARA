import { useState } from 'react'
import Button from './Button'
import { CheckOutlined, CloseOutlined, SyncOutlined } from '@ant-design/icons'

export default function ApprovalPanel({ proposal, campaignId, onApprove, onReject, onRevise }) {
  const [feedback, setFeedback] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleApprove() {
    setLoading(true)
    await onApprove()
    setLoading(false)
  }

  async function handleReject() {
    setLoading(true)
    await onReject()
    setLoading(false)
  }

  async function handleRevise() {
    if (!feedback.trim()) return
    setLoading(true)
    await onRevise(feedback.trim())
    setLoading(false)
  }

  return (
    <div className="approval-panel">
      <div className="approval-title">
        ⏳ Awaiting Your Approval
      </div>
      <div className="approval-subtitle">
        Review the campaign proposal below and approve, request revisions, or reject.
      </div>

      {proposal && (
        <div className="approval-proposal">{proposal}</div>
      )}

      <div className="approval-feedback">
        <textarea
          placeholder="Optional: add revision notes or feedback before requesting changes..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="approval-actions">
        <Button
          variant="success"
          size="sm"
          onClick={handleApprove}
          disabled={loading}
        >
          <CheckOutlined /> Approve
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRevise}
          disabled={loading || !feedback.trim()}
        >
          <SyncOutlined /> Request Revisions
        </Button>
        <Button
          variant="danger"
          size="sm"
          onClick={handleReject}
          disabled={loading}
        >
          <CloseOutlined /> Reject
        </Button>
      </div>
    </div>
  )
}
