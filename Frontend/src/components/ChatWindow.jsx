import { useState, useEffect, useCallback } from 'react'
import { RocketOutlined } from '@ant-design/icons'
import Greeting from './Greeting'
import ChatInput from './ChatInput'
import MessageList from './MessageList'
import LiveStreamView from './LiveStreamView'
import CampaignBriefForm from './CampaignBriefForm'
import ApprovalPanel from './ApprovalPanel'
import Button from './Button'
import { useToast } from './Toast'
import WebSocketService from '../services/WebSocketService'
import { api } from '../services/api'

const NODE_MESSAGES = {
  input_validator: { complete: 'Brief validated successfully.' },
  brief_analyst: { complete: 'Brief analysis complete. Identified goals and channel fit.' },
  campaign_architect: { complete: 'Campaign plan created with phases and messaging hierarchy.' },
  channel_expander: { complete: 'Channel-specific task templates expanded.' },
  task_assembler: { complete: 'All tasks assembled with dependencies and suggested owners.' },
  proposal_formatter: { complete: 'Campaign proposal formatted and ready for review.' },
  approval_handler: {
    complete: 'Approval processed.',
    waiting: null, // handled specially via ApprovalPanel
    error: 'Approval process encountered an error.',
  },
  revision_parser: { complete: 'Revisions parsed. Feeding changes back to Campaign Architect.' },
  metrics_fetcher: { complete: 'Performance metrics fetched from analytics sources.' },
  insights_synthesizer: { complete: 'Performance insights synthesized. Report ready.' },
}

const DOMAIN_LABELS = {
  planner: '🧠 Planner',
  comms: '📨 Comms',
  analytics: '📊 Analytics',
  pre_graph: '✅ Pre-Graph',
}

let msgIdCounter = 0
function newId() {
  return ++msgIdCounter
}

function buildMsg(role, content, extra = {}) {
  return { id: newId(), role, content, timestamp: new Date().toISOString(), ...extra }
}

export default function ChatWindow({ activeView, resetKey, externalSplit, onCampaignStarted }) {
  const toast = useToast()
  const [messages, setMessages] = useState([])
  const [streamEvents, setStreamEvents] = useState([])
  const [streamText, setStreamText] = useState('')
  const [split, setSplit] = useState(false)
  const [connected, setConnected] = useState(false)
  const [campaignStatus, setCampaignStatus] = useState('idle') // idle | running | waiting_approval | complete | error
  const [currentCampaign, setCurrentCampaign] = useState(null) // { campaign_id, session_id }
  const [pendingProposal, setPendingProposal] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [initialContext, setInitialContext] = useState('')

  const splitVisible = split || externalSplit

  // Reset everything when resetKey changes
  useEffect(() => {
    WebSocketService.disconnect()
    setMessages([])
    setStreamEvents([])
    setStreamText('')
    setConnected(false)
    setCampaignStatus('idle')
    setCurrentCampaign(null)
    setPendingProposal('')
    setShowForm(false)
    setInitialContext('')
  }, [resetKey])

  // Force split when Live Stream tab active
  useEffect(() => {
    if (activeView === 'Live Stream') setSplit(true)
  }, [activeView])

  const appendMessage = useCallback((msg) => {
    setMessages((prev) => [...prev, msg])
  }, [])

  const removeTyping = useCallback(() => {
    setMessages((prev) => prev.filter((m) => !m.isTyping))
  }, [])

  function handleWsMessage(data) {
    // Handle plain text chunks
    if (data.type === 'text') {
      setStreamText((t) => t + data.text)
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last && last.role === 'assistant' && last.isStreaming) {
          return [...prev.slice(0, -1), { ...last, content: last.content + data.text }]
        }
        return [
          ...prev,
          buildMsg('assistant', data.text, { isStreaming: true }),
        ]
      })
      return
    }

    // WSEvent objects from the graph
    const { node, status, domain, payload, error_message, timestamp } = data

    // Add to live stream events (cap at 200)
    setStreamEvents((prev) => [
      { node, status, domain, timestamp, error_message },
      ...prev.slice(0, 199),
    ])

    // Remove typing indicator before showing node message
    removeTyping()

    // Handle assistant_chunk / assistant_done from older backends
    if (data.type === 'assistant_chunk') {
      setStreamText((t) => t + (data.text || ''))
      return
    }
    if (data.type === 'assistant_done') return

    // Map node events to chat messages
    const nodeMsg = NODE_MESSAGES[node]

    if (node === 'approval_handler' && status === 'waiting') {
      const proposal = payload?.proposal || ''
      setPendingProposal(proposal)
      setCampaignStatus('waiting_approval')
      appendMessage(
        buildMsg('system', `📨 Proposal sent for review. Awaiting your approval below.`)
      )
      toast.warning('Campaign proposal ready — your approval is required.')
      return
    }

    if (nodeMsg) {
      const text = nodeMsg[status]
      if (text) {
        const domain_label = DOMAIN_LABELS[domain] || domain
        appendMessage(
          buildMsg('assistant', `[${domain_label}] ${text}`)
        )
      }
    }

    // Handle special payloads
    if (node === 'insights_synthesizer' && status === 'complete' && payload?.report) {
      appendMessage(
        buildMsg('assistant', formatReport(payload.report))
      )
    }

    if (status === 'error' && error_message) {
      appendMessage(
        buildMsg('system', `⚠️ Error in ${node}: ${error_message}`)
      )
      setCampaignStatus('error')
      toast.error(`Pipeline error in ${node}: ${error_message}`)
    }

    // Check for graph completion
    if (data.status === 'complete' && !node) {
      setCampaignStatus('complete')
      appendMessage(
        buildMsg('assistant', '✅ Campaign pipeline complete! All tasks have been processed.')
      )
      toast.success('Campaign pipeline completed successfully!')
    }
  }

  function formatReport(report) {
    if (typeof report === 'string') return report
    try {
      const lines = ['📊 Performance Report\n']
      if (report.summary) lines.push(`Summary: ${report.summary}`)
      if (report.recommendations?.length) {
        lines.push('\nRecommendations:')
        report.recommendations.forEach((r, i) => lines.push(`  ${i + 1}. ${r}`))
      }
      return lines.join('\n')
    } catch {
      return JSON.stringify(report, null, 2)
    }
  }

  async function handleFormSubmit(brief) {
    setShowForm(false)
    appendMessage(buildMsg('user', `🚀 Campaign: "${brief.campaign_name}"\nObjective: ${brief.objective}\nAudience: ${brief.target_audience}\nChannels: ${brief.channels.join(', ')}\nDuration: ${brief.duration_days} days`))
    appendMessage(buildMsg('assistant', '', { isTyping: true }))

    try {
      const result = await api.runCampaign(brief)
      const { campaign_id, session_id } = result
      setCurrentCampaign({ campaign_id, session_id })
      setCampaignStatus('running')
      setSplit(true)

      removeTyping()
      appendMessage(buildMsg('assistant', `Campaign launched! Session ID: ${session_id}\n\nThe MARA pipeline is now running. Watch the live stream panel for real-time agent events.`))
      onCampaignStarted?.({ campaign_id, session_id, name: brief.campaign_name })

      toast.success(`Campaign "${brief.campaign_name}" launched!`)

      // Connect WebSocket
      WebSocketService.connect(session_id, {
        onMessage: handleWsMessage,
        onStatusChange: (s) => {
          const isConnected = s === 'connected'
          setConnected(isConnected)
          if (isConnected) {
            toast.info('Connected to live agent stream.')
          } else if (s === 'disconnected') {
            toast.warning('Live stream disconnected.')
          } else if (s === 'error') {
            toast.error('Live stream connection error.')
          }
        },
      })
    } catch (err) {
      removeTyping()
      appendMessage(buildMsg('system', `⚠️ Failed to launch campaign: ${err.message}`))
      setCampaignStatus('idle')
      toast.error(`Failed to launch campaign: ${err.message}`)
    }
  }

  function handleChatSend(text) {
    if (campaignStatus === 'idle') {
      setInitialContext(text)
      setShowForm(true)
      return
    }

    if (campaignStatus === 'waiting_approval') {
      // Treat plain message as revision request
      appendMessage(buildMsg('user', text))
      handleRevise(text)
      return
    }

    // General message while running (informational)
    appendMessage(buildMsg('user', text))
    appendMessage(buildMsg('assistant', "The campaign pipeline is running. Check the live stream panel for real-time updates."))
  }

  async function handleApprove() {
    if (!currentCampaign) return
    appendMessage(buildMsg('user', '✅ I approve this campaign proposal.'))
    setCampaignStatus('running')
    setPendingProposal('')
    try {
      await api.approveCampaign(currentCampaign.campaign_id, 'approve')
      appendMessage(buildMsg('assistant', '[📨 Comms] Approval confirmed. Proceeding to analytics phase...'))
      toast.success('Campaign approved — proceeding to analytics.')
    } catch (err) {
      appendMessage(buildMsg('system', `⚠️ Approval failed: ${err.message}`))
      toast.error(`Approval failed: ${err.message}`)
    }
  }

  async function handleReject() {
    if (!currentCampaign) return
    appendMessage(buildMsg('user', '❌ I am rejecting this campaign proposal.'))
    setCampaignStatus('complete')
    setPendingProposal('')
    try {
      await api.approveCampaign(currentCampaign.campaign_id, 'reject')
      appendMessage(buildMsg('assistant', 'Campaign proposal rejected. Pipeline terminated.'))
      toast.info('Campaign proposal rejected. Pipeline terminated.')
    } catch (err) {
      appendMessage(buildMsg('system', `⚠️ Rejection failed: ${err.message}`))
      toast.error(`Rejection failed: ${err.message}`)
    }
  }

  async function handleRevise(feedback) {
    if (!currentCampaign) return
    appendMessage(buildMsg('user', `🔄 Revision request: ${feedback}`))
    setCampaignStatus('running')
    setPendingProposal('')
    try {
      await api.approveCampaign(currentCampaign.campaign_id, 'revise', feedback)
      appendMessage(buildMsg('assistant', '[📨 Comms] Revision request recorded. Routing back to Campaign Architect...'))
      toast.info('Revision request submitted — re-routing to Campaign Architect.')
    } catch (err) {
      appendMessage(buildMsg('system', `⚠️ Revision request failed: ${err.message}`))
      toast.error(`Revision request failed: ${err.message}`)
    }
  }

  const hasMessages = messages.length > 0
  const isIdle = campaignStatus === 'idle' && !hasMessages

  const inputPlaceholder =
    campaignStatus === 'waiting_approval'
      ? 'Type revision notes or use the approval panel below...'
      : campaignStatus === 'running'
      ? 'Campaign is running...'
      : 'Describe your campaign to get started...'

  const inputDisabled = campaignStatus === 'running'

  return (
    <div style={{ display: 'flex', flex: 1, gap: 10, minWidth: 0, overflow: 'hidden' }}>
      <div className="chat-window">
        {/* Toolbar */}
        <div className="chat-toolbar">
          <div className="stream-label">
            <div className={`stream-label-dot ${connected ? 'connected' : ''}`} />
            {connected ? 'Live' : campaignStatus === 'idle' ? 'Offline' : 'Disconnected'}
            {currentCampaign && (
              <span style={{ color: '#555', fontSize: 11, fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>
                · {currentCampaign.campaign_id.slice(0, 8)}
              </span>
            )}
          </div>
          <div className="toolbar-right">
            <span className="toolbar-label">Live Stream</span>
            <div
              className={`split-toggle ${splitVisible ? 'active' : ''}`}
              onClick={() => setSplit((s) => !s)}
              role="switch"
              aria-checked={splitVisible}
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setSplit((s) => !s)}
            >
              <div className="split-toggle-thumb" />
            </div>
          </div>
        </div>

        {/* Body */}
        {isIdle && !showForm ? (
          <div className="center-stage">
            <Greeting user="Marketer" mode="centered" />
            <Button
              variant="primary"
              size="lg"
              onClick={() => setShowForm(true)}
            >
              <RocketOutlined /> Launch New Campaign
            </Button>
          </div>
        ) : isIdle && showForm ? (
          <div className="center-stage">
            <CampaignBriefForm
              onSubmit={handleFormSubmit}
              onCancel={() => setShowForm(false)}
              initialContext={initialContext}
            />
          </div>
        ) : (
          <div className="messages-area">
            <MessageList messages={messages} />

            {campaignStatus === 'waiting_approval' && pendingProposal !== undefined && (
              <ApprovalPanel
                proposal={pendingProposal}
                campaignId={currentCampaign?.campaign_id}
                onApprove={handleApprove}
                onReject={handleReject}
                onRevise={handleRevise}
              />
            )}

            <ChatInput
              onSend={handleChatSend}
              disabled={inputDisabled}
              placeholder={inputPlaceholder}
            />
          </div>
        )}
      </div>

      {/* Live Stream Panel */}
      {splitVisible && (
        <LiveStreamView
          events={streamEvents}
          streamText={streamText}
          onClear={() => {
            setStreamEvents([])
            setStreamText('')
            toast.info('Live stream cleared.')
          }}
        />
      )}
    </div>
  )
}
