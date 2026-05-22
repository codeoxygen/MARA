const BASE = '/api'

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  runCampaign(brief) {
    return post('/campaigns/run', brief)
  },
  getCampaign(campaignId) {
    return get(`/campaigns/${campaignId}`)
  },
  approveCampaign(campaignId, action = 'approve', feedback = '') {
    const params = new URLSearchParams({ action })
    if (feedback) params.set('feedback', feedback)
    return fetch(`${BASE}/campaigns/${campaignId}/approve?${params}`, {
      method: 'POST',
    }).then((r) => r.json())
  },
  resumeCampaign(campaignId, approvalResponse) {
    return post(`/campaigns/${campaignId}/resume`, approvalResponse)
  },
}
