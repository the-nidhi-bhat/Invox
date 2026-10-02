import React, { useState } from 'react'
import { extractOrder } from '../services/mockExtractor.js'

const EXAMPLE = 'bhaiya 50 mouse 450 wala, Acme Pune ko, 5% gst laga dena'

/**
 * OrderComposer
 *
 * Props:
 *   onExtractionStart()                   — called when submission begins
 *   onExtractionSuccess(result, message)  — called with ExtractionResult + original message
 *   onExtractionError(error)              — called on failure
 */
export default function OrderComposer({ onExtractionStart, onExtractionSuccess, onExtractionError }) {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [fieldError, setFieldError] = useState('')

  function validate(text) {
    if (!text.trim()) return 'Please enter an order message.'
    if (text.trim().length < 5) return 'Order message is too short.'
    return ''
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const error = validate(message)
    if (error) { setFieldError(error); return }
    setFieldError('')
    setLoading(true)
    onExtractionStart()
    try {
      const result = await extractOrder(message)
      onExtractionSuccess(result, message.trim())
    } catch (err) {
      onExtractionError(err)
    } finally {
      setLoading(false)
    }
  }

  function handleChange(e) {
    setMessage(e.target.value)
    if (fieldError) setFieldError('')
  }

  function fillExample() {
    setMessage(EXAMPLE)
    setFieldError('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate>
      {/* Label */}
      <label htmlFor="order-message" className="sr-only">
        Order message
      </label>

      {/* Textarea */}
      <div className="relative">
        <textarea
          id="order-message"
          name="order-message"
          className={[
            'w-full min-h-[120px] rounded-xl bg-gray-800 border text-gray-100 text-sm p-4 pr-4',
            'placeholder-gray-600 resize-none focus:outline-none focus:ring-2',
            'focus:ring-brand-500 focus:border-transparent transition leading-relaxed',
            fieldError ? 'border-red-500' : 'border-gray-700',
          ].join(' ')}
          placeholder={'Type or paste your order — e.g. \u201cbhaiya 50 mouse 450 wala, Acme Pune ko, 5% gst laga dena\u201d'}
          value={message}
          onChange={handleChange}
          disabled={loading}
          aria-describedby={fieldError ? 'order-error' : undefined}
          aria-invalid={!!fieldError}
          autoComplete="off"
          spellCheck="false"
        />
      </div>

      {/* Validation error */}
      {fieldError && (
        <p id="order-error" role="alert" className="text-xs text-red-400 -mt-1">
          {fieldError}
        </p>
      )}

      {/* Footer row */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <button
          type="button"
          onClick={fillExample}
          disabled={loading}
          className="text-xs text-gray-500 hover:text-brand-500 underline underline-offset-2
                     transition disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none
                     focus:ring-2 focus:ring-brand-500 rounded"
        >
          Use example order
        </button>

        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-brand-500 hover:bg-brand-600
                     active:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed
                     text-white text-sm font-semibold transition
                     focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2
                     focus:ring-offset-gray-900"
        >
          {loading ? (
            <>
              <svg className="w-4 h-4 animate-spin shrink-0" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Preparing…
            </>
          ) : (
            <>
              <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
              Extract Order
            </>
          )}
        </button>
      </div>
    </form>
  )
}
