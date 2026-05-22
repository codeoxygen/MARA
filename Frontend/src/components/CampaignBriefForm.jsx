import { useState, useRef } from 'react'
import {
  RocketOutlined,
  FlagOutlined,
  TeamOutlined,
  CalendarOutlined,
  DollarOutlined,
  BulbOutlined,
  BarChartOutlined,
  FileTextOutlined,
  LinkedinOutlined,
  MailOutlined,
  InstagramOutlined,
  SearchOutlined,
  FacebookOutlined,
  TwitterOutlined,
  YoutubeOutlined,
  MobileOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  CloseOutlined,
} from '@ant-design/icons'

const CHANNELS = [
  { id: 'LinkedIn',    Icon: LinkedinOutlined },
  { id: 'Email',       Icon: MailOutlined },
  { id: 'Instagram',   Icon: InstagramOutlined },
  { id: 'Paid Search', Icon: SearchOutlined },
  { id: 'Facebook',    Icon: FacebookOutlined },
  { id: 'Twitter/X',   Icon: TwitterOutlined },
  { id: 'YouTube',     Icon: YoutubeOutlined },
  { id: 'TikTok',      Icon: MobileOutlined },
]

const DEFAULT_FORM = {
  campaign_name: '',
  objective: '',
  target_audience: '',
  channels: [],
  duration_days: '',
  budget: '',
  key_messages: [],
  success_metrics: [],
  additional_context: '',
}

/* ── Reusable tag-list input ────────────────────────── */
function TagInput({ items, onChange, placeholder }) {
  const [draft, setDraft] = useState('')
  const inputRef = useRef(null)

  function add() {
    const val = draft.trim()
    if (!val) return
    onChange([...items, val])
    setDraft('')
    inputRef.current?.focus()
  }

  function remove(idx) {
    onChange(items.filter((_, i) => i !== idx))
  }

  function onKey(e) {
    if (e.key === 'Enter') { e.preventDefault(); add() }
  }

  return (
    <div className="cbf-tag-input">
      <div className="cbf-tag-row">
        <input
          ref={inputRef}
          className="cbf-input cbf-tag-draft"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKey}
          placeholder={placeholder}
        />
        <button
          type="button"
          className={`cbf-tag-add ${draft.trim() ? 'cbf-tag-add--active' : ''}`}
          onClick={add}
          aria-label="Add item"
        >
          <PlusOutlined />
        </button>
      </div>

      {items.length > 0 && (
        <ul className="cbf-tag-list">
          {items.map((item, idx) => (
            <li key={idx} className="cbf-tag-item">
              <span className="cbf-tag-index">{idx + 1}</span>
              <span className="cbf-tag-text">{item}</span>
              <button
                type="button"
                className="cbf-tag-remove"
                onClick={() => remove(idx)}
                aria-label="Remove"
              >
                <CloseOutlined />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

/* ── Section header ─────────────────────────────────── */
function SectionHeader({ icon, title, subtitle }) {
  return (
    <div className="cbf-section-header">
      <span className="cbf-section-icon">{icon}</span>
      <div>
        <div className="cbf-section-title">{title}</div>
        {subtitle && <div className="cbf-section-subtitle">{subtitle}</div>}
      </div>
    </div>
  )
}

/* ── Generic field wrapper ──────────────────────────── */
function Field({ label, required, error, icon, children }) {
  return (
    <div className={`cbf-field ${error ? 'cbf-field--error' : ''}`}>
      {label !== '' && (
        <label className="cbf-label">
          {icon && <span className="cbf-label-icon">{icon}</span>}
          {label}
          {required && <span className="cbf-required">*</span>}
        </label>
      )}
      {children}
      {error && (
        <div className="cbf-field-error">
          <ExclamationCircleOutlined style={{ fontSize: 11 }} />
          {error}
        </div>
      )}
    </div>
  )
}

/* ── Main form ──────────────────────────────────────── */
export default function CampaignBriefForm({ onSubmit, onCancel, initialContext = '' }) {
  const [form, setForm] = useState({ ...DEFAULT_FORM, additional_context: initialContext })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  function setField(key, value) {
    setForm((f) => ({ ...f, [key]: value }))
    if (errors[key]) setErrors((e) => ({ ...e, [key]: '' }))
  }

  function toggleChannel(ch) {
    setForm((f) => ({
      ...f,
      channels: f.channels.includes(ch)
        ? f.channels.filter((c) => c !== ch)
        : [...f.channels, ch],
    }))
    if (errors.channels) setErrors((e) => ({ ...e, channels: '' }))
  }

  function validate() {
    const e = {}
    if (!form.campaign_name.trim())   e.campaign_name   = 'Campaign name is required.'
    if (!form.objective.trim())       e.objective       = 'Objective is required.'
    if (!form.target_audience.trim()) e.target_audience = 'Target audience is required.'
    if (form.channels.length === 0)   e.channels        = 'Select at least one channel.'
    if (!form.duration_days || isNaN(Number(form.duration_days)) || Number(form.duration_days) < 1)
      e.duration_days = 'Enter a valid number of days.'
    return e
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setLoading(true)
    try {
      await onSubmit({
        campaign_name:      form.campaign_name.trim(),
        objective:          form.objective.trim(),
        target_audience:    form.target_audience.trim(),
        channels:           form.channels,
        duration_days:      Number(form.duration_days),
        budget:             form.budget ? Number(form.budget) : undefined,
        key_messages:       form.key_messages.length ? form.key_messages : undefined,
        success_metrics:    form.success_metrics.length ? form.success_metrics : undefined,
        additional_context: form.additional_context.trim() || undefined,
      })
    } catch (err) {
      setErrors({ _form: err.message || 'Failed to launch campaign.' })
      setLoading(false)
    }
  }

  return (
    <form className="cbf" onSubmit={handleSubmit} noValidate>

      {/* ── Header ── */}
      <div className="cbf-header">
        <div className="cbf-header-icon"><RocketOutlined /></div>
        <div>
          <div className="cbf-title">Launch Campaign</div>
          <div className="cbf-subtitle">Fill in your marketing brief to start the MARA pipeline</div>
        </div>
      </div>

      <div className="cbf-body">

        {/* ── 1: Campaign Basics ── */}
        <div className="cbf-section">
          <SectionHeader icon={<FlagOutlined />} title="Campaign Basics" />

          <div className="cbf-row-2">
            <Field label="Campaign Name" required error={errors.campaign_name}>
              <input
                className="cbf-input"
                placeholder="e.g. Q3 Brand Awareness"
                value={form.campaign_name}
                onChange={(e) => setField('campaign_name', e.target.value)}
              />
            </Field>
            <Field label="Duration" required error={errors.duration_days} icon={<CalendarOutlined />}>
              <div className="cbf-input-suffix-wrap">
                <input
                  className="cbf-input"
                  type="number"
                  placeholder="30"
                  min={1}
                  value={form.duration_days}
                  onChange={(e) => setField('duration_days', e.target.value)}
                />
                <span className="cbf-input-suffix-label">days</span>
              </div>
            </Field>
          </div>

          <Field label="Objective" required error={errors.objective} icon={<BulbOutlined />}>
            <input
              className="cbf-input"
              placeholder="e.g. Increase brand awareness among SMB decision-makers"
              value={form.objective}
              onChange={(e) => setField('objective', e.target.value)}
            />
          </Field>

          <Field label="Target Audience" required error={errors.target_audience} icon={<TeamOutlined />}>
            <input
              className="cbf-input"
              placeholder="e.g. B2B SaaS founders, 25–45, North America"
              value={form.target_audience}
              onChange={(e) => setField('target_audience', e.target.value)}
            />
          </Field>
        </div>

        {/* ── 2: Channels ── */}
        <div className="cbf-section">
          <SectionHeader
            icon={<BarChartOutlined />}
            title="Channels"
            subtitle="Select all that apply"
          />
          <div className={`cbf-channels ${errors.channels ? 'cbf-channels--error' : ''}`}>
            {CHANNELS.map(({ id, Icon }) => (
              <button
                key={id}
                type="button"
                className={`cbf-chip ${form.channels.includes(id) ? 'cbf-chip--on' : ''}`}
                onClick={() => toggleChannel(id)}
              >
                <Icon className="cbf-chip-icon" />
                {id}
              </button>
            ))}
          </div>
          {errors.channels && (
            <div className="cbf-field-error" style={{ marginTop: 6 }}>
              <ExclamationCircleOutlined style={{ fontSize: 11 }} />
              {errors.channels}
            </div>
          )}
        </div>

        {/* ── 3: Budget & Goals ── */}
        <div className="cbf-section">
          <SectionHeader
            icon={<DollarOutlined />}
            title="Budget & Goals"
            subtitle="Optional — helps MARA optimise the plan"
          />

          {/* Budget alone on its row */}
          <Field label="Budget" icon={<DollarOutlined />}>
            <div className="cbf-input-prefix-wrap">
              <span className="cbf-input-prefix-label">$</span>
              <input
                className="cbf-input cbf-input--prefixed"
                type="number"
                placeholder="15 000"
                min={0}
                value={form.budget}
                onChange={(e) => setField('budget', e.target.value)}
              />
            </div>
          </Field>

          {/* Key Messages + Success Metrics side by side */}
          <div className="cbf-row-2 cbf-row-2--top">
            <Field label="Key Messages" icon={<BulbOutlined />}>
              <TagInput
                items={form.key_messages}
                onChange={(v) => setField('key_messages', v)}
                placeholder="e.g. Drive qualified leads"
              />
            </Field>

            <Field label="Success Metrics" icon={<BarChartOutlined />}>
              <TagInput
                items={form.success_metrics}
                onChange={(v) => setField('success_metrics', v)}
                placeholder="e.g. 10% CTR increase"
              />
            </Field>
          </div>
        </div>

        {/* ── 4: Additional Context ── */}
        <div className="cbf-section">
          <SectionHeader
            icon={<FileTextOutlined />}
            title="Additional Context"
            subtitle="Optional — constraints, tone of voice, or notes"
          />
          <Field label="">
            <textarea
              className="cbf-input cbf-textarea"
              placeholder="Brand voice is professional but approachable. Avoid competitor mentions..."
              value={form.additional_context}
              onChange={(e) => setField('additional_context', e.target.value)}
              rows={3}
            />
          </Field>
        </div>

      </div>{/* end cbf-body */}

      {/* ── Form-level error ── */}
      {errors._form && (
        <div className="cbf-form-error">
          <ExclamationCircleOutlined />
          {errors._form}
        </div>
      )}

      {/* ── Actions ── */}
      <div className="cbf-actions">
        {onCancel && (
          <button type="button" className="cbf-btn cbf-btn--ghost" onClick={onCancel}>
            Cancel
          </button>
        )}
        <button type="submit" className="cbf-btn cbf-btn--launch" disabled={loading}>
          <RocketOutlined />
          {loading ? 'Launching…' : 'Launch Campaign'}
        </button>
      </div>

    </form>
  )
}
