import { useEffect, useState } from 'react'
import { STAGES } from './data/stages'
import {
  analyzeCall,
  closeCall,
  createCall,
  getCall,
  listCalls,
  saveCallStage,
} from './services/api'
import './App.css'

const responseExamples = {
  2: [
    'From where? Can you say it again?',
    'Regarding?',
    'I’m listening.',
  ],
}

const responseCategories = [
  'Asked what this is about',
  'Asked who I am',
  'Ready to hear more',
  'Asked me to call later',
]

const outcomes = [
  ['next_step_agreed', 'Next step agreed'],
  ['agreed_to_receive_report', 'Agreed to receive information'],
  ['follow_up', 'Follow-up requested'],
  ['interested', 'Interested'],
  ['not_interested', 'Not interested'],
  ['do_not_call', 'Do not call'],
  ['wrong_person', 'Wrong person'],
  ['moved_company', 'Moved company'],
  ['call_again', 'Call again'],
  ['no_answer', 'No answer'],
  ['unknown', 'Unknown / not logged'],
]

const intentLabels = {
  asking_purpose: 'Asking about the call',
  available_now: 'Available to talk',
  busy_requesting_callback: 'Busy or requesting a callback',
  providing_business_context: 'Sharing business context',
  describing_business_need: 'Describing a business need',
  requesting_information: 'Requesting information',
  expressing_interest: 'Expressing interest',
  raising_objection: 'Raising a concern',
  declining: 'Declining',
  do_not_call: 'Do not call',
  wrong_contact_or_referral: 'Wrong contact or referral',
  language_or_connection_issue: 'Language or connection issue',
  agreeing_next_step: 'Agreeing to a next step',
  unclear: 'Unclear',
}

function stagePayload(entry = {}) {
  return {
    response_category: entry.category || null,
    prospect_words: entry.prospectWords || null,
    notes: entry.notes || null,
  }
}

async function persistStage(callId, stageNumber, entry, setSaveStatus, setApiError) {
  setSaveStatus('Saving…')
  try {
    await saveCallStage(callId, stageNumber, stagePayload(entry))
    setSaveStatus('Saved')
    setApiError('')
    return true
  } catch (error) {
    setSaveStatus('Save failed')
    setApiError(error.message)
    return false
  }
}

function formatOutcome(value) {
  return outcomes.find(([key]) => key === value)?.[1] || 'Not logged'
}

function formatDate(value) {
  if (!value) return 'Date unavailable'
  return new Date(value).toLocaleString()
}

function formatIntent(value) {
  return intentLabels[value] || 'Unclear'
}

function App() {
  const [view, setView] = useState('history')
  const [calls, setCalls] = useState([])
  const [activeCall, setActiveCall] = useState(null)
  const [prospectName, setProspectName] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [currentStageIndex, setCurrentStageIndex] = useState(0)
  const [stageEntries, setStageEntries] = useState({})
  const [showEndCall, setShowEndCall] = useState(false)
  const [selectedOutcome, setSelectedOutcome] = useState('')
  const [saveStatus, setSaveStatus] = useState('')
  const [busy, setBusy] = useState(false)
  const [apiError, setApiError] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    let isMounted = true
    listCalls()
      .then((result) => {
        if (isMounted) setCalls(result.calls || [])
      })
      .catch((error) => {
        if (isMounted) setApiError(error.message)
      })
    return () => {
      isMounted = false
    }
  }, [])

  const currentStage = STAGES[currentStageIndex]
  const currentEntry = stageEntries[currentStage.number] ?? {
    category: '',
    prospectWords: '',
    notes: '',
  }
  const nextStage = STAGES[currentStageIndex + 1]
  const progress = ((currentStageIndex + 1) / STAGES.length) * 100
  const examples = responseExamples[currentStage.number] ?? []
  const readOnly = activeCall?.status === 'completed'

  useEffect(() => {
    if (!activeCall || view !== 'call' || readOnly) return undefined
    const entry = stageEntries[currentStage.number]
    if (!entry || (!entry.category && !entry.prospectWords.trim() && !entry.notes.trim())) {
      return undefined
    }

    const timer = window.setTimeout(() => {
      persistStage(activeCall.id, currentStage.number, entry, setSaveStatus, setApiError)
    }, 650)
    return () => window.clearTimeout(timer)
  }, [activeCall, currentStage, readOnly, stageEntries, view])

  async function refreshCalls() {
    const result = await listCalls()
    setCalls(result.calls || [])
  }

  async function handleStartCall(event) {
    event.preventDefault()
    setBusy(true)
    setApiError('')
    try {
      const call = await createCall({
        prospect_name: prospectName.trim(),
        company_name: companyName.trim() || null,
      })
      setCalls((existing) => [call, ...existing.filter((item) => item.id !== call.id)])
      setActiveCall(call)
      setStageEntries({})
      setCurrentStageIndex(0)
      setSelectedOutcome('')
      setAnalysis(null)
      setSaveStatus('Call started')
      setView('call')
    } catch (error) {
      setApiError(error.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleOpenCall(callId) {
    setBusy(true)
    setApiError('')
    try {
      const call = await getCall(callId)
      const entries = Object.fromEntries(
        (call.call_stages || []).map((stage) => [stage.stage_number, {
          category: stage.response_category || '',
          prospectWords: stage.prospect_words || '',
          notes: stage.notes || '',
        }]),
      )
      setActiveCall(call)
      setStageEntries(entries)
      setCurrentStageIndex(Math.max(0, Math.min(STAGES.length - 1, (call.last_stage || 1) - 1)))
      setSelectedOutcome(call.outcome || '')
      setAnalysis(null)
      setSaveStatus(call.status === 'completed' ? 'Completed' : 'Call resumed')
      setView('call')
    } catch (error) {
      setApiError(error.message)
    } finally {
      setBusy(false)
    }
  }

  function updateCurrentEntry(changes) {
    setStageEntries((entries) => ({
      ...entries,
      [currentStage.number]: {
        ...currentEntry,
        ...changes,
      },
    }))
  }

  async function navigateToStage(index) {
    if (index === currentStageIndex || !activeCall) {
      setCurrentStageIndex(index)
      return
    }
    if (!readOnly) {
      const saved = await persistStage(
        activeCall.id,
        currentStage.number,
        currentEntry,
        setSaveStatus,
        setApiError,
      )
      if (!saved) return
    }
    setAnalysis(null)
    setCurrentStageIndex(index)
  }

  async function handleAnalyzeCall() {
    if (!activeCall) return
    setAnalyzing(true)
    setApiError('')
    setAnalysis(null)
    try {
      const result = await analyzeCall(
        activeCall.id,
        currentStage.number,
        currentEntry.prospectWords,
      )
      setAnalysis(result)
    } catch (error) {
      setApiError(error.message)
    } finally {
      setAnalyzing(false)
    }
  }

  async function handleCloseCall() {
    if (!activeCall || !selectedOutcome) return
    setBusy(true)
    setApiError('')
    try {
      if (!readOnly) {
        const stageSaved = await persistStage(
          activeCall.id,
          currentStage.number,
          currentEntry,
          setSaveStatus,
          setApiError,
        )
        if (!stageSaved) return
      }
      await closeCall(activeCall.id, selectedOutcome)
      setShowEndCall(false)
      setSelectedOutcome('')
      setActiveCall(null)
      setView('history')
      await refreshCalls()
    } catch (error) {
      setApiError(error.message)
    } finally {
      setBusy(false)
    }
  }

  async function goToHistory() {
    if (activeCall && !readOnly) {
      const saved = await persistStage(
        activeCall.id,
        currentStage.number,
        currentEntry,
        setSaveStatus,
        setApiError,
      )
      if (!saved) return
    }
    setView('history')
    setActiveCall(null)
    setApiError('')
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">C</span>
          <div>
            <p className="eyebrow">MERIDIAN GROWTH PARTNERS</p>
            <h1>Call guide</h1>
          </div>
        </div>
        {view === 'call' && activeCall ? (
          <div className="call-header-actions">
            <span className={readOnly ? 'save-status completed' : 'save-status'}>
              {readOnly ? 'COMPLETED' : saveStatus || 'IN PROGRESS'}
            </span>
            <button className="text-button" onClick={goToHistory}>Call history</button>
          </div>
        ) : (
          <span className="preview-status">CALL HISTORY</span>
        )}
      </header>

      {apiError && (
        <div className="error-banner" role="alert">
          <span>{apiError}</span>
          <button className="text-button" onClick={() => setApiError('')}>Dismiss</button>
        </div>
      )}

      {view === 'history' ? (
        <>
          <section className="start-card">
            <p className="eyebrow">START A CALL</p>
            <h2>Who are you calling?</h2>
            <form className="start-call-form" onSubmit={handleStartCall}>
              <label>
                <span>Prospect name</span>
                <input
                  value={prospectName}
                  onChange={(event) => setProspectName(event.target.value)}
                  placeholder="Name of the person"
                  maxLength={200}
                  required
                />
              </label>
              <label>
                <span>Company <em>Optional</em></span>
                <input
                  value={companyName}
                  onChange={(event) => setCompanyName(event.target.value)}
                  placeholder="Company name"
                  maxLength={200}
                />
              </label>
              <button className="primary-button" type="submit" disabled={busy || !prospectName.trim()}>
                {busy ? 'Starting…' : 'Start call'}
              </button>
            </form>
          </section>

          <section className="history-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">PAST CALLS</p>
                <h2>Call history</h2>
              </div>
              <button className="secondary-button" onClick={() => refreshCalls().catch((error) => setApiError(error.message))} disabled={busy}>
                Refresh
              </button>
            </div>
            {calls.length === 0 ? (
              <p className="empty-history">No saved calls yet. Start a call above to see it here.</p>
            ) : (
              <div className="call-list">
                {calls.map((call) => (
                  <button
                    key={call.id}
                    className="call-list-item"
                    onClick={() => handleOpenCall(call.id)}
                    disabled={busy}
                  >
                    <span className="call-list-main">
                      <strong>{call.prospect_name || 'Unnamed prospect'}</strong>
                      <span>{call.company_name || 'Company not recorded'}</span>
                      <small>{formatDate(call.started_at)}</small>
                    </span>
                    <span className="call-list-meta">
                      <span className={call.status === 'completed' ? 'list-status completed' : 'list-status'}>
                        {call.status === 'completed' ? 'Completed' : 'In progress'}
                      </span>
                      <span>Stage {call.last_stage || 1} · {formatOutcome(call.outcome)}</span>
                      <span>{call.duration_seconds == null ? 'Duration not recorded' : `${call.duration_seconds}s`}</span>
                    </span>
                  </button>
                ))}
              </div>
            )}
          </section>
        </>
      ) : activeCall ? (
        <>
          <section className="call-context" aria-label="Call details">
            <div>
              <p className="eyebrow">PROSPECT</p>
              <p className="context-value">
                {activeCall.prospect_name}{activeCall.company_name ? ` · ${activeCall.company_name}` : ''}
              </p>
            </div>
            <p className="context-note">Started {formatDate(activeCall.started_at)}</p>
          </section>

          <nav className="stage-navigation" aria-label="Call stages">
            {STAGES.map((stage, index) => (
              <button
                key={stage.number}
                className={index === currentStageIndex ? 'stage-button active' : 'stage-button'}
                aria-label={`Stage ${stage.number}: ${stage.name}`}
                aria-current={index === currentStageIndex ? 'step' : undefined}
                onClick={() => navigateToStage(index)}
              >
                {stage.number}
              </button>
            ))}
          </nav>

          <div
            className="progress-track"
            role="progressbar"
            aria-label="Call stage progress"
            aria-valuemin={1}
            aria-valuemax={STAGES.length}
            aria-valuenow={currentStage.number}
          >
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>

          <section className="stage-card">
            <p className="eyebrow stage-count">STAGE {currentStage.number} OF {STAGES.length}</p>
            <h2>{currentStage.name}</h2>
            <div className="purpose-block">
              <h3>Purpose</h3>
              <p>{currentStage.purpose}</p>
            </div>

            <section className="examples-block" aria-labelledby="examples-title">
              <h3 id="examples-title">They may say</h3>
              {examples.length > 0 ? (
                <ul className="example-list">
                  {examples.map((example) => <li key={example}>“{example}”</li>)}
                </ul>
              ) : (
                <p className="coming-soon">Examples for this stage will be drawn from the supplied calls.</p>
              )}
            </section>

            <section className="response-block" aria-labelledby="response-title">
              <h3 id="response-title">What happened?</h3>
              <div className="response-options">
                {responseCategories.map((category) => (
                  <button
                    key={category}
                    className={currentEntry.category === category ? 'response-chip selected' : 'response-chip'}
                    aria-pressed={currentEntry.category === category}
                    onClick={() => updateCurrentEntry({ category })}
                    disabled={readOnly}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </section>

            <label className="words-field">
              <span>Prospect’s words</span>
              <textarea
                value={currentEntry.prospectWords}
                onChange={(event) => updateCurrentEntry({ prospectWords: event.target.value })}
                placeholder="Capture their words as closely as you can…"
                rows={4}
                disabled={readOnly}
              />
            </label>
            <details className="notes-details">
              <summary> Add an optional note</summary>
              <textarea
                value={currentEntry.notes}
                onChange={(event) => updateCurrentEntry({ notes: event.target.value })}
                placeholder="Add context for your team…"
                rows={2}
                disabled={readOnly}
              />
            </details>

            <section className="ai-assist-block" aria-labelledby="ai-assist-title" aria-live="polite">
              <div className="ai-assist-heading">
                <div>
                  <h3 id="ai-assist-title">Optional response suggestions</h3>
                  <p>Uses these words and earlier saved stages when Gemini is configured. You stay in control.</p>
                </div>
                <button
                  className="secondary-button"
                  onClick={handleAnalyzeCall}
                  disabled={readOnly || analyzing || !currentEntry.prospectWords.trim()}
                >
                  {analyzing ? 'Thinking…' : 'Get suggestions'}
                </button>
              </div>
              {analysis && (
                <div className="ai-analysis">
                  <p className="ai-source">
                    {analysis.source === 'gemini' ? 'Gemini suggestions' : 'Fallback suggestions · Gemini unavailable'}
                    {' · '}Uncertainty: {analysis.uncertainty}
                  </p>
                  <p className="ai-likely-stage">
                    Likely stage: {STAGES.find((stage) => stage.number === analysis.likely_stage_number)?.name || 'Unknown'}
                  </p>
                  <p className="ai-likely-stage">Likely intent: {formatIntent(analysis.likely_intent)}</p>
                  <p className="ai-explanation">{analysis.explanation}</p>
                  <ol>
                    {analysis.suggested_responses.map((suggestion, index) => (
                      <li key={`${index}-${suggestion}`}>{suggestion}</li>
                    ))}
                  </ol>
                  {analysis.recommended_next_action && (
                    <p className="ai-next-action">
                      <strong>Possible next action:</strong> {analysis.recommended_next_action}
                    </p>
                  )}
                </div>
              )}
            </section>
          </section>

          <footer className="stage-controls">
            <button
              className="secondary-button"
              onClick={() => navigateToStage(Math.max(0, currentStageIndex - 1))}
              disabled={currentStageIndex === 0 || busy}
            >
              Previous
            </button>
            <div className="footer-actions">
              {!readOnly && (
                <button className="end-button" onClick={() => setShowEndCall(true)} disabled={busy}>
                  End call
                </button>
              )}
              <button
                className="primary-button"
                onClick={() => navigateToStage(Math.min(STAGES.length - 1, currentStageIndex + 1))}
                disabled={!nextStage || busy}
              >
                {nextStage ? `Next: ${nextStage.name}` : 'Last stage'}
              </button>
            </div>
          </footer>
        </>
      ) : null}

      {showEndCall && (
        <div className="dialog-backdrop">
          <section className="outcome-dialog" role="dialog" aria-modal="true" aria-labelledby="outcome-title">
            <button className="dialog-close" onClick={() => setShowEndCall(false)} aria-label="Cancel ending the call">×</button>
            <p className="eyebrow">END CALL</p>
            <h2 id="outcome-title">Choose the call outcome</h2>
            <p className="dialog-note">The caller chooses the outcome. The call can end at any stage.</p>
            <label className="outcome-field">
              <span>Outcome</span>
              <select value={selectedOutcome} onChange={(event) => setSelectedOutcome(event.target.value)}>
                <option value="">Select an outcome</option>
                {outcomes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <button className="primary-button dialog-submit" onClick={handleCloseCall} disabled={!selectedOutcome || busy}>
              {busy ? 'Saving…' : 'End call and save outcome'}
            </button>
          </section>
        </div>
      )}
    </main>
  )
}

export default App
