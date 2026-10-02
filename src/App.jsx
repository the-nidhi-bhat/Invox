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
 *   'idle'      — empty state, waiting for input
 *   'loading'   — extraction in progress (mock or future real API)
 *   'review'    — extraction complete, seller reviews/edits extracted fields
 *   'confirmed' — seller confirmed order (M3+ will trigger invoice generation here)
 *   'error'     — extraction failed
 *
 * M3 will add: confirmed → invoice generation → invoice display.
 * InvoicePreview (from M1) will be re-wired in M6.
 */
export default function App() {
  const [uiState, setUiState] = useState('idle')  // 'idle' | 'loading' | 'review' | 'confirmed' | 'error'
  const [submittedMessage, setSubmittedMessage] = useState('')
  const [extraction, setExtraction] = useState(null)
  const [extractionError, setExtractionError] = useState('')
  const [confirmedOrder, setConfirmedOrder] = useState(null)

  function handleExtractionStart() {
    setUiState('loading')
    setExtraction(null)
    setExtractionError('')
    setConfirmedOrder(null)
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

  function handleConfirm(draft) {
    setConfirmedOrder(draft)
    setUiState('confirmed')
  }

  function handleReset() {
    setUiState('idle')
    setSubmittedMessage('')
    setExtraction(null)
    setExtractionError('')
    setConfirmedOrder(null)
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
      case 'confirmed':
        return (
          <div className="rounded-2xl bg-gray-900 border border-green-800/40 p-8 flex flex-col items-center gap-4 text-center">
            <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm">Order confirmed</h3>
              <p className="text-gray-500 text-xs mt-1 max-w-[240px]">
                Invoice generation will be wired here in Milestone 6.
              </p>
            </div>
            {confirmedOrder && (
              <div className="w-full bg-gray-800/60 rounded-xl px-4 py-3 text-left">
                <p className="text-xs text-gray-500 mb-2 font-medium">Confirmed order</p>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                  <dt className="text-gray-500">Customer</dt>
                  <dd className="text-gray-200">{confirmedOrder.customer}</dd>
                  <dt className="text-gray-500">Location</dt>
                  <dd className="text-gray-200">{confirmedOrder.location}</dd>
                  <dt className="text-gray-500">Product</dt>
                  <dd className="text-gray-200">{confirmedOrder.items[0].name}</dd>
                  <dt className="text-gray-500">Qty</dt>
                  <dd className="text-gray-200">{confirmedOrder.items[0].quantity}</dd>
                  <dt className="text-gray-500">Unit price</dt>
                  <dd className="text-gray-200">₹{confirmedOrder.items[0].unitPrice}</dd>
                  <dt className="text-gray-500">Stated GST</dt>
                  <dd className="text-gray-200">{confirmedOrder.statedGstRate}%</dd>
                </dl>
              </div>
            )}
            <button
              type="button"
              onClick={handleReset}
              className="text-xs text-brand-500 hover:text-brand-400 underline underline-offset-2
                         transition focus:outline-none focus:ring-2 focus:ring-brand-500 rounded"
            >
              Start new order
            </button>
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
              <h3 className="text-white font-semibold text-sm">Could not process order</h3>
              <p className="text-gray-400 text-xs mt-1 max-w-[280px] leading-relaxed">
                {extractionError}
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
