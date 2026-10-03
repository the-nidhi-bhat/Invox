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
export default function OrderComposer({ onExtractionStart, onExtractionSuccess, onExtractionError, disabled = false }) {
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

  const isDisabled = loading || disabled

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3" noValidate aria-busy={isDisabled}>
      <div className="field-group">
        <label htmlFor="order-message" className="label">Order message</label>
        <textarea
          id="order-message"
          name="order-message"
          className={[
            'input min-h-[176px] resize-y leading-relaxed',
            fieldError && 'input-error',
          ].join(' ')}
          placeholder='For example: 50 mouse at ₹450 each, Acme in Pune, 5% GST'
          value={message}
          onChange={handleChange}
          disabled={isDisabled}
          aria-describedby={fieldError ? 'order-hint order-error' : 'order-hint'}
          aria-invalid={!!fieldError}
          autoComplete="off"
          spellCheck="true"
        />
        <p id="order-hint" className="text-xs leading-relaxed text-text-muted">
          Paste a customer order in English or Hinglish. You can review every extracted detail before continuing.
        </p>
      </div>

      {/* Validation error */}
      {fieldError && (
        <p id="order-error" role="alert" className="field-error">
          {fieldError}
        </p>
      )}

      {/* Footer row */}
      <div className="flex flex-col-reverse items-stretch justify-between gap-3 sm:flex-row sm:items-center">
        <button
          type="button"
          onClick={fillExample}
          disabled={isDisabled}
          className="btn-ghost btn-sm whitespace-nowrap text-xs"
        >
          Use example order
        </button>

        <button
          type="submit"
          disabled={isDisabled || !message.trim()}
          className="btn-primary btn-md whitespace-nowrap sm:min-w-40"
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
