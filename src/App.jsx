import React, { useState } from 'react'
import Header from './components/Header.jsx'
import OrderComposer from './components/OrderComposer.jsx'
import LoadingState from './components/LoadingState.jsx'
import ExtractionReview from './components/ExtractionReview.jsx'
import EmptyState from './components/EmptyState.jsx'

/**
 * App — INVOX root component.
 *
 * UI state machine:
 *
 *   'idle'        — empty state, waiting for input
 *   'loading'     — extraction in progress (mock or future real API)
 *   'review'      — extraction complete, seller reviews/edits extracted fields
 *   'calculating' — deterministic GST calculation in progress
 *   'confirmed'   — GST calculated, seller sees final breakdown
 *   'error'       — extraction/calculation failed
 *
 * M6 adds: confirmed → deterministic GST calculation → confirmed with breakdown
 */
export default function App() {
  const [uiState, setUiState] = useState('idle')  // 'idle' | 'loading' | 'review' | 'calculating' | 'confirmed' | 'error'
  const [submittedMessage, setSubmittedMessage] = useState('')
  const [extraction, setExtraction] = useState(null)
  const [extractionError, setExtractionError] = useState('')
  const [confirmedOrder, setConfirmedOrder] = useState(null)
  const [gstResult, setGstResult] = useState(null)
  const [gstError, setGstError] = useState('')

  function handleExtractionStart() {
    setUiState('loading')
    setExtraction(null)
    setExtractionError('')
    setConfirmedOrder(null)
    setGstResult(null)
    setGstError('')
  }

  function handleExtractionSuccess(result, message) {
    setSubmittedMessage(message)
    setExtraction(result)
    setUiState('review')
  }

  function handleExtractionError(err) {
    setExtractionError(err?.message ?? 'Extraction failed. Please try again.')
    setUiState('error')
  }

  async function handleConfirm(draft) {
    setConfirmedOrder(draft)
    setUiState('calculating')
    setGstError('')

    try {
      // Call deterministic GST calculation endpoint
      const response = await fetch('/gst/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_state: draft.location,
          items: draft.items.map(item => ({
            name: item.name,
            quantity: item.quantity,
            unit_price: item.unitPrice,
            stated_gst_rate: draft.statedGstRate,
          })),
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error ?? 'GST calculation failed')
      }

      setGstResult(data)
      setUiState('confirmed')
    } catch (err) {
      setGstError(err?.message ?? 'GST calculation failed. Please try again.')
      setUiState('error')
    }
  }

  function handleReset() {
    setUiState('idle')
    setSubmittedMessage('')
    setExtraction(null)
    setExtractionError('')
    setConfirmedOrder(null)
    setGstResult(null)
    setGstError('')
  }

  // Determine what to render in the right panel
  function renderRightPanel() {
    switch (uiState) {
      case 'loading':
        return <LoadingState message={submittedMessage} />
      case 'review':
        return (
          <ExtractionReview
            originalMessage={submittedMessage}
            extraction={extraction}
            onConfirm={handleConfirm}
            onReset={handleReset}
          />
        )
      case 'calculating':
        return (
          <div className="rounded-2xl bg-gray-900 border border-yellow-800/40 p-8 flex flex-col items-center gap-4 text-center">
            <div className="w-12 h-12 rounded-full bg-yellow-500/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-yellow-400 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm">Calculating GST</h3>
              <p className="text-gray-500 text-xs mt-1 max-w-[280px]">
                Applying deterministic tax rules…
              </p>
            </div>
          </div>
        )
      case 'confirmed':
        return (
          <div className="flex flex-col gap-4">
            {gstResult?.gst_mismatch && (
              <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-4 flex items-start gap-3">
                <svg className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
                <div className="flex-1">
                  <p className="text-xs font-semibold text-amber-400">GST rate mismatch detected</p>
                  <p className="text-xs text-amber-300 mt-1">
                    Message stated <span className="font-semibold">{gstResult.stated_gst_rate ?? 'no'}%</span> GST,
                    but deterministic rules determine <span className="font-semibold">{gstResult.determined_gst_rate}%</span>.
                    Calculation uses the <span className="font-semibold">determined rate</span>.
                  </p>
                </div>
              </div>
            )}

            <div className="rounded-2xl bg-gray-900 border border-green-800/40 p-5 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-semibold text-sm">GST Calculation Complete</h3>
                  <p className="text-gray-500 text-xs mt-1">
                    Deterministic rules applied. AI proposed. Rules decided.
                  </p>
                </div>
                <span className="text-xs px-2 py-0.5 rounded border border-green-700 text-green-400 shrink-0">
                  {gstResult?.tax_type === 'intra_state' ? 'Intra-state (CGST+SGST)' : 'Inter-state (IGST)'}
                </span>
              </div>

              <div className="rounded-xl bg-gray-800/60 border border-gray-800 p-4 flex flex-col gap-3">
                <p className="text-xs text-gray-500 font-medium uppercase tracking-widest">Items</p>
                <div className="flex flex-col gap-2">
                  {gstResult?.items?.map((item, idx) => (
                    <div key={idx} className="rounded-lg bg-gray-800/50 p-3 flex flex-col sm:flex-row sm:items-center gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white">{item.name}</p>
                        <p className="text-xs text-gray-500">
                          Qty: {item.quantity} × ₹{item.unit_price}
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-right">
                        <div>
                          <p className="text-gray-500">Subtotal</p>
                          <p className="text-white">₹{item.subtotal.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">GST ({item.gst_rate}%)</p>
                          <p className="text-white">₹{item.gst_amount.toFixed(2)}</p>
                        </div>
                        {item.tax_type === 'intra_state' ? (
                          <>
                            <div>
                              <p className="text-gray-500">CGST ({item.cgst_rate}%)</p>
                              <p className="text-white">₹{item.cgst_amount.toFixed(2)}</p>
                            </div>
                            <div>
                              <p className="text-gray-500">SGST ({item.sgst_rate}%)</p>
                              <p className="text-white">₹{item.sgst_amount.toFixed(2)}</p>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="sm:col-span-2">
                              <p className="text-gray-500">IGST ({item.igst_rate}%)</p>
                              <p className="text-white">₹{item.igst_amount.toFixed(2)}</p>
                            </div>
                            <div className="sm:hidden" />
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl bg-gray-800/60 border border-gray-800 p-4 flex flex-col gap-2">
                <p className="text-xs text-gray-500 font-medium uppercase tracking-widest">Totals</p>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                  <dt className="text-gray-500">Subtotal</dt>
                  <dd className="text-gray-200 text-right">₹{gstResult?.total_subtotal.toFixed(2)}</dd>
                  <dt className="text-gray-500">Total GST</dt>
                  <dd className="text-gray-200 text-right">₹{gstResult?.total_gst_amount.toFixed(2)}</dd>
                  {gstResult?.tax_type === 'intra_state' ? (
                    <>
                      <dt className="text-gray-500">CGST</dt>
                      <dd className="text-gray-200 text-right">₹{gstResult?.total_cgst.toFixed(2)}</dd>
                      <dt className="text-gray-500">SGST</dt>
                      <dd className="text-gray-200 text-right">₹{gstResult?.total_sgst.toFixed(2)}</dd>
                    </>
                  ) : (
                    <>
                      <dt className="text-gray-500">IGST</dt>
                      <dd className="text-gray-200 text-right">₹{gstResult?.total_igst.toFixed(2)}</dd>
                    </>
                  )}
                  <dt className="text-gray-500 font-semibold">Grand Total</dt>
                  <dd className="text-white font-semibold text-right">₹{gstResult?.grand_total.toFixed(2)}</dd>
                </dl>
              </div>

              <div className="rounded-lg bg-green-500/10 border border-green-500/30 p-3 text-center">
                <p className="text-xs text-green-400">
                  Calculation uses deterministic rules. AI proposed the extraction; rules decided the tax.
                </p>
              </div>

              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2.5 rounded-lg border border-gray-700 text-gray-400 text-sm font-medium
                           hover:border-gray-600 hover:text-gray-300 transition
                           focus:outline-none focus:ring-2 focus:ring-gray-600"
              >
                Start new order
              </button>
            </div>
          </div>
        )
      case 'error':
        return (
          <div className="rounded-2xl bg-gray-900 border border-red-800/40 p-8 flex flex-col items-center gap-4 text-center">
            <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm">
                {gstError ? 'GST calculation failed' : 'Could not process order'}
              </h3>
              <p className="text-gray-400 text-xs mt-1 max-w-[280px] leading-relaxed">
                {gstError || extractionError}
              </p>
            </div>
            <button
              type="button"
              onClick={handleReset}
              className="px-4 py-2 rounded-lg border border-gray-700 text-gray-300 text-xs
                         hover:border-gray-600 transition focus:outline-none focus:ring-2
                         focus:ring-gray-600"
            >
              Try again
            </button>
          </div>
        )
      default: // 'idle'
        return <EmptyState />
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-950">
      <Header />

      <main className="flex-1 flex flex-col lg:flex-row gap-6 p-4 md:p-6 max-w-7xl mx-auto w-full">

        {/* Left panel — Order input */}
        <section className="flex flex-col gap-4 lg:w-1/2" aria-label="Order input">
          <div className="rounded-2xl bg-gray-900 border border-gray-800 p-5 flex flex-col gap-3">
            <div>
              <h2 className="text-sm font-semibold text-gray-200">
                New order
              </h2>
              <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                Describe the order naturally — in English or Hinglish. INVOX will
                extract the details for you to review.
              </p>
            </div>
            <OrderComposer
              onExtractionStart={() => {
                // Capture the message before it gets cleared
                handleExtractionStart()
              }}
              onExtractionSuccess={handleExtractionSuccess}
              onExtractionError={handleExtractionError}
            />
          </div>

          {/* Workflow indicator */}
          <WorkflowSteps currentState={uiState} />
        </section>

        {/* Right panel — dynamic content */}
        <section className="lg:w-1/2" aria-label="Extraction result and review">
          {renderRightPanel()}
        </section>

      </main>
    </div>
  )
}

/**
 * WorkflowSteps — lightweight visual progress indicator.
 * Shows the seller where they are in the order→invoice flow.
 */
function WorkflowSteps({ currentState }) {
  const steps = [
    { id: 'idle',      label: 'Enter order' },
    { id: 'loading',   label: 'Extract' },
    { id: 'review',    label: 'Review' },
    { id: 'confirmed', label: 'Invoice' },
  ]

  const activeIndex = steps.findIndex(s => s.id === currentState)

  return (
    <div className="flex items-center gap-0" aria-label="Workflow progress" role="list">
      {steps.map((step, i) => {
        const done = i < activeIndex
        const active = i === activeIndex
        return (
          <React.Fragment key={step.id}>
            <div
              className="flex items-center gap-1.5"
              role="listitem"
              aria-current={active ? 'step' : undefined}
            >
              <div className={[
                'w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition',
                done    ? 'bg-brand-500 text-white' :
                active  ? 'bg-brand-500/20 border border-brand-500 text-brand-500' :
                          'bg-gray-800 border border-gray-700 text-gray-600',
              ].join(' ')}>
                {done ? (
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  i + 1
                )}
              </div>
              <span className={[
                'text-xs transition',
                active ? 'text-gray-200 font-medium' : done ? 'text-gray-400' : 'text-gray-600',
              ].join(' ')}>
                {step.label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={[
                'flex-1 h-px mx-2 transition',
                i < activeIndex ? 'bg-brand-500/40' : 'bg-gray-800',
              ].join(' ')} aria-hidden="true" />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}
