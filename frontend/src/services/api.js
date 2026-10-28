const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(data?.detail || `Request failed (${response.status})`)
  }

  return data
}

export function createCall(callDetails) {
  return request('/calls', {
    method: 'POST',
    body: JSON.stringify(callDetails),
  })
}

export function listCalls() {
  return request('/calls')
}

export function getCall(callId) {
  return request(`/calls/${encodeURIComponent(callId)}`)
}

export function saveCallStage(callId, stageNumber, stageDetails) {
  return request(`/calls/${encodeURIComponent(callId)}/stages/${stageNumber}`, {
    method: 'PUT',
    body: JSON.stringify(stageDetails),
  })
}

export function analyzeCall(callId, stageNumber, prospectWords) {
  return request(`/calls/${encodeURIComponent(callId)}/analyze`, {
    method: 'POST',
    body: JSON.stringify({ stage_number: stageNumber, prospect_words: prospectWords }),
  })
}

export function closeCall(callId, outcome) {
  return request(`/calls/${encodeURIComponent(callId)}/close`, {
    method: 'POST',
    body: JSON.stringify({ outcome }),
  })
}
