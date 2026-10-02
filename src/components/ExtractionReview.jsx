import React, { useState } from 'react'

/**
 * ExtractionReview
 *
 * Displays the structured extraction result for the seller to review and edit.
 * All fields are editable. Changes are local until the user proceeds to invoice
 * generation (M6+).
 *
 * The component intentionally does NOT calculate GST or final totals.
 * Those are the backend's responsibility (M5).
 *
 * Props:
 *   originalMessage  — the raw order text entered by the seller
 *   extraction       — ExtractionResult from mockExtractor (or future API)
 *   onConfirm(draft) — called with the edited draft when the seller confirms
 *   onReset()        — called when the seller wants to start over
 */
export default function ExtractionReview({ originalMessage, extraction, onConfirm, onReset }) {
  const item0 = extraction.items?.[0] ?? {}

  const [draft, setDraft] = useState({
    customer: extraction.customer ?? '',
    location: extraction.location ?? '',
    itemName: item0.name ?? '',
    quantity: String(item0.quantity ?? ''),
    unitPrice: String(item0.unitPrice ?? ''),
    statedGstRate: String(extraction.statedGstRate ?? ''),
  })

  const [errors, setErrors] = useState({})

  function updateField(field, value) {
    setDraft(prev => ({ ...prev, [field]: value }))
    if (errors[field]) setErrors(prev => ({ ...prev, [field]: '' }))
  }

  function validate() {
    const e = {}
    if (!draft.customer.trim()) e.customer = 'Required'
    if (!draft.location.trim()) e.location = 'Required'
    if (!draft.itemName.trim()) e.itemName = 'Required'
    const qty = Number(draft.quantity)
    if (!draft.quantity.trim() || isNaN(qty) || qty <= 0 || !Number.isInteger(qty)) {
      e.quantity = 'Must be a positive whole number'
    }
    const price = Number(draft.unitPrice)
    if (!draft.unitPrice.trim() || isNaN(price) || price < 0) {
      e.unitPrice = 'Must be a valid amount (0 or more)'
    }
    const gst = Number(draft.statedGstRate)
    if (!draft.statedGstRate.trim() || isNaN(gst) || gst < 0 || gst > 100) {
      e.statedGstRate = 'Must be a percentage between 0 and 100'
    }
    return e
  }

  function handleConfirm() {
    const e = validate()
    if (Object.keys(e).length > 0) { setErrors(e); return }
    onConfirm({
      customer: draft.customer.trim(),
      location: draft.location.trim(),
      items: [{
        name: draft.itemName.trim(),
        quantity: Number(draft.quantity),
        unitPrice: Number(draft.unitPrice),
      }],
      statedGstRate: Number(draft.statedGstRate),
    })
  }

  return (
    <div className="flex flex-col gap-4">

      {/* Original message */}
      <div className="bg-gray-800/60 rounded-xl px-4 py-3">
        <p className="text-xs text-gray-500 mb-1">Original message</p>
        <p className="text-sm text-gray-300 italic leading-relaxed">"{originalMessage}"</p>
      </div>

      {/* Review card */}
      <div className="rounded-2xl bg-gray-900 border border-gray-800 overflow-hidden">

        {/* Card header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
          <div>
            <h2 className="text-sm font-semibold text-white">Review extracted order</h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Edit any field, then confirm to continue.
            </p>
          </div>
          {extraction.source === 'mock' && (
            <span className="text-xs px-2 py-0.5 rounded border border-gray-700 text-gray-500 shrink-0">
              Demo data
            </span>
          )}
        </div>

        {/* Notice */}
        <div className="px-5 py-3 bg-yellow-500/5 border-b border-yellow-500/10 flex items-start gap-2">
          <svg className="w-4 h-4 text-yellow-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
          <p className="text-xs text-yellow-400 leading-relaxed">
            <span className="font-semibold">Review before continuing.</span>{' '}
            The stated GST rate is what appeared in the message — it is NOT the validated rate.
            GST rules are applied by the backend in a later step.
          </p>
        </div>

        {/* Fields */}
        <div className="px-5 py-4 flex flex-col gap-4">

          {/* Customer + Location row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field
              id="customer"
              label="Customer"
              value={draft.customer}
              error={errors.customer}
              onChange={v => updateField('customer', v)}
              placeholder="Customer name"
            />
            <Field
              id="location"
              label="Location"
              value={draft.location}
              error={errors.location}
              onChange={v => updateField('location', v)}
              placeholder="City or state"
            />
          </div>

          {/* Divider */}
          <div className="border-t border-gray-800" aria-hidden="true" />
          <p className="text-xs text-gray-500 font-medium uppercase tracking-widest -mb-1">Items</p>

          {/* Item name */}
          <Field
            id="item-name"
            label="Product"
            value={draft.itemName}
            error={errors.itemName}
            onChange={v => updateField('itemName', v)}
            placeholder="Product or service name"
          />

          {/* Qty + Price row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field
              id="quantity"
              label="Quantity"
              value={draft.quantity}
              error={errors.quantity}
              onChange={v => updateField('quantity', v)}
              placeholder="e.g. 50"
              inputMode="numeric"
            />
            <Field
              id="unit-price"
              label="Unit price (₹)"
              value={draft.unitPrice}
              error={errors.unitPrice}
              onChange={v => updateField('unitPrice', v)}
              placeholder="e.g. 450"
              inputMode="decimal"
            />
          </div>

          {/* Divider */}
          <div className="border-t border-gray-800" aria-hidden="true" />

          {/* GST rate */}
          <div>
            <Field
              id="stated-gst"
              label="Stated GST rate (%)"
              value={draft.statedGstRate}
              error={errors.statedGstRate}
              onChange={v => updateField('statedGstRate', v)}
              placeholder="e.g. 5"
              inputMode="decimal"
            />
            <p className="text-xs text-gray-600 mt-1.5">
              This is what the message stated. The backend will validate and apply the correct rate.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="px-5 py-4 border-t border-gray-800 flex flex-col sm:flex-row gap-3">
          <button
            type="button"
            onClick={onReset}
            className="flex-1 sm:flex-none px-4 py-2.5 rounded-lg border border-gray-700
                       text-gray-400 text-sm font-medium hover:border-gray-600 hover:text-gray-300
                       transition focus:outline-none focus:ring-2 focus:ring-gray-600"
          >
            Start over
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            className="flex-1 py-2.5 rounded-lg bg-brand-500 hover:bg-brand-600 active:bg-brand-700
                       text-white text-sm font-semibold transition
                       focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2
                       focus:ring-offset-gray-900"
          >
            Confirm order →
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * Field — reusable labelled input for the review form.
 */
function Field({ id, label, value, error, onChange, placeholder, inputMode }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-xs font-medium text-gray-400">
        {label}
      </label>
      <input
        id={id}
        type="text"
        inputMode={inputMode}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={[
          'rounded-lg bg-gray-800 border text-gray-100 text-sm px-3 py-2',
          'focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition',
          error ? 'border-red-500' : 'border-gray-700',
        ].join(' ')}
      />
      {error && (
        <p id={`${id}-error`} role="alert" className="text-xs text-red-400">
          {error}
        </p>
      )}
    </div>
  )
}
