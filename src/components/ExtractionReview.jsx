import React, { useState, useEffect } from 'react'

/**
 * ExtractionReview
 *
 * Displays the structured extraction result for the seller to review and edit.
 * All fields are editable. Changes are local until the user proceeds to invoice
 * generation (M6+).
 *
 * The component intentionally does NOT calculate GST or final totals.
 * Those are the backend's responsibility (M6).
 *
 * Props:
 *   originalMessage  — the raw order text entered by the seller
 *   extraction       — ExtractionResult from mockExtractor (or future API)
 *   onConfirm(draft) — called with the edited draft when the seller confirms
 *   onReset()        — called when the seller wants to start over
 */
export default function ExtractionReview({ originalMessage, extraction, onConfirm, onReset }) {
  const source = extraction?.source ?? 'mock'
  const initialItems = extraction?.items?.length > 0
    ? extraction.items
    : [{ name: '', quantity: '', unitPrice: '' }]

  const [draft, setDraft] = useState({
    customer: extraction?.customer ?? '',
    location: extraction?.location ?? '',
    items: initialItems.map(item => ({
      name: item.name ?? '',
      quantity: String(item.quantity ?? ''),
      unitPrice: String(item.unitPrice ?? ''),
    })),
    statedGstRate: String(extraction?.statedGstRate ?? ''),
  })

  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})

  // Track which fields have been edited by human
  const [humanEdited, setHumanEdited] = useState({})

  function updateField(field, value, index = null) {
    setDraft(prev => {
      if (index !== null && field === 'items') {
        const newItems = [...prev.items]
        newItems[index] = { ...newItems[index], ...value }
        return { ...prev, items: newItems }
      }
      return { ...prev, [field]: value }
    })
    // Clear error when user types
    if (errors[field] || (index !== null && errors[`items.${index}.${field}`])) {
      setErrors(prev => {
        const next = { ...prev }
        if (index !== null) {
          delete next[`items.${index}.${field}`]
        } else {
          delete next[field]
        }
        return next
      })
    }
    // Mark as human-edited
    const editKey = index !== null ? `items.${index}.${field}` : field
    setHumanEdited(prev => ({ ...prev, [editKey]: true }))
  }

  function markTouched(field, index = null) {
    const touchKey = index !== null ? `items.${index}.${field}` : field
    setTouched(prev => ({ ...prev, [touchKey]: true }))
  }

  function validate() {
    const e = {}

    // Customer - optional, but if provided must not be empty string (handled by trim)
    // Location - optional

    // Items validation
    if (!draft.items || draft.items.length === 0) {
      e.items = 'At least one item is required'
    } else {
      draft.items.forEach((item, idx) => {
        if (!item.name?.trim()) {
          e[`items.${idx}.name`] = 'Product name is required'
        }
        const qty = Number(item.quantity)
        if (!item.quantity?.trim() || isNaN(qty) || qty <= 0 || !Number.isInteger(qty)) {
          e[`items.${idx}.quantity`] = 'Must be a positive whole number'
        }
        const price = Number(item.unitPrice)
        if (!item.unitPrice?.trim() || isNaN(price) || price < 0) {
          e[`items.${idx}.unitPrice`] = 'Must be a valid amount (0 or more)'
        }
      })
    }

    // Stated GST rate - optional but if provided must be valid
    if (draft.statedGstRate?.trim()) {
      const gst = Number(draft.statedGstRate)
      if (isNaN(gst) || gst < 0 || gst > 100) {
        e.statedGstRate = 'Must be a percentage between 0 and 100'
      }
    }

    return e
  }

  function handleAddItem() {
    setDraft(prev => ({
      ...prev,
      items: [...prev.items, { name: '', quantity: '', unitPrice: '' }],
    }))
  }

  function handleRemoveItem(index) {
    if (draft.items.length <= 1) return // Keep at least one
    setDraft(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }))
  }

  function handleConfirm() {
    const e = validate()
    if (Object.keys(e).length > 0) {
      setErrors(e)
      return
    }
    // Filter out items with empty names (shouldn't happen due to validation)
    const validItems = draft.items.filter(item => item.name?.trim())
    onConfirm({
      customer: draft.customer.trim(),
      location: draft.location.trim(),
      items: validItems.map(item => ({
        name: item.name.trim(),
        quantity: Number(item.quantity),
        unitPrice: Number(item.unitPrice),
      })),
      statedGstRate: draft.statedGstRate?.trim() ? Number(draft.statedGstRate) : null,
    })
  }

  // Determine source label for badge
  const sourceLabels = {
    mock: 'Demo data',
    bedrock: 'AI extracted',
    placeholder: 'Not implemented',
  }

  return (
    <div className="flex flex-col gap-4">

      {/* Original message */}
      <div className="bg-surface-elevated/60 rounded-xl px-4 py-3">
        <p className="text-xs text-text-muted mb-1">Original message</p>
        <p className="text-sm text-text-secondary italic leading-relaxed">"{originalMessage}"</p>
      </div>

      {/* Review card */}
      <div className="card overflow-hidden">

        {/* Card header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div>
            <h2 className="text-sm font-semibold text-text-primary">Review extracted order</h2>
            <p className="text-xs text-text-muted mt-0.5">
              Edit any field, then confirm to continue.
            </p>
          </div>
          <span className="badge-neutral shrink-0">
            {sourceLabels[source] ?? 'Unknown source'}
          </span>
        </div>

        {/* Notice */}
        <div className="px-5 py-3 bg-status-warning/5 border-b border-status-warning/10 flex items-start gap-2">
          <svg className="w-4 h-4 text-status-warning mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
          <p className="text-xs text-status-warning leading-relaxed">
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
              label="Customer (optional)"
              value={draft.customer}
              error={touched.customer && errors.customer}
              onChange={v => updateField('customer', v)}
              onBlur={() => markTouched('customer')}
              placeholder="Customer name"
              isEdited={humanEdited.customer}
            />
            <Field
              id="location"
              label="Location (optional)"
              value={draft.location}
              error={touched.location && errors.location}
              onChange={v => updateField('location', v)}
              onBlur={() => markTouched('location')}
              placeholder="City or state"
              isEdited={humanEdited.location}
            />
          </div>

          {/* Divider */}
          <div className="border-t border-border" aria-hidden="true" />
          <p className="text-xs text-text-muted font-medium uppercase tracking-widest -mb-1">Items</p>

          {/* Items list */}
          <div className="flex flex-col gap-3">
            {draft.items.map((item, idx) => (
              <ItemRow
                key={idx}
                index={idx}
                item={item}
                errors={errors}
                touched={touched}
                humanEdited={humanEdited}
                onUpdate={(field, value) => updateField(field, value, idx)}
                onBlur={(field) => markTouched(field, idx)}
                onRemove={() => handleRemoveItem(idx)}
                canRemove={draft.items.length > 1}
                isFirst={idx === 0}
              />
            ))}
            {draft.items.length < 5 && (
              <button
                type="button"
                onClick={handleAddItem}
                className="w-full py-2 text-center text-xs text-brand-500 hover:text-brand-400 border border-dashed border-border rounded-lg transition"
              >
                + Add another item
              </button>
            )}
          </div>

          {/* Divider */}
          <div className="border-t border-border" aria-hidden="true" />

          {/* GST rate */}
          <div>
            <Field
              id="stated-gst"
              label="Stated GST rate (%) — optional"
              value={draft.statedGstRate}
              error={touched['stated-gst'] && errors.statedGstRate}
              onChange={v => updateField('statedGstRate', v)}
              onBlur={() => markTouched('stated-gst')}
              placeholder="e.g. 5"
              inputMode="decimal"
              isEdited={humanEdited.statedGstRate}
            />
            <p className="text-xs text-text-muted mt-1.5">
              This is what the message stated. The backend will validate and apply the correct rate.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="px-5 py-4 border-t border-border flex flex-col sm:flex-row gap-3">
          <button
            type="button"
            onClick={onReset}
            className="btn-secondary btn-md"
          >
            Start over
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            className="btn-primary btn-md"
          >
            Confirm order →
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * ItemRow — a single editable item row in the review form.
 */
function ItemRow({ index, item, errors, touched, humanEdited, onUpdate, onBlur, onRemove, canRemove, isFirst }) {
  const itemErrors = errors[`items.${index}`] || {}
  const itemTouched = touched[`items.${index}`] || {}
  const itemEdited = humanEdited[`items.${index}`] || {}

  return (
    <div className="flex flex-col sm:flex-row gap-3 items-start">
      <div className="flex-1 min-w-0">
        <Field
          id={`item-name-${index}`}
          label={isFirst ? 'Product' : 'Product'}
          value={item.name}
          error={itemTouched.name && itemErrors.name}
          onChange={v => onUpdate('name', v)}
          onBlur={() => onBlur('name')}
          placeholder="Product or service name"
          isEdited={itemEdited.name}
        />
      </div>
      <div className="grid grid-cols-2 gap-3 w-full sm:w-auto">
        <Field
          id={`quantity-${index}`}
          label="Qty"
          value={item.quantity}
          error={itemTouched.quantity && itemErrors.quantity}
          onChange={v => onUpdate('quantity', v)}
          onBlur={() => onBlur('quantity')}
          placeholder="e.g. 50"
          inputMode="numeric"
          isEdited={itemEdited.quantity}
        />
        <Field
          id={`unit-price-${index}`}
          label="Unit price (₹)"
          value={item.unitPrice}
          error={itemTouched.unitPrice && itemErrors.unitPrice}
          onChange={v => onUpdate('unitPrice', v)}
          onBlur={() => onBlur('unitPrice')}
          placeholder="e.g. 450"
          inputMode="decimal"
          isEdited={itemEdited.unitPrice}
        />
      </div>
      {canRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="self-end px-3 py-2 text-xs text-text-muted hover:text-status-error border border-border hover:border-status-error rounded-lg transition"
          aria-label={`Remove item ${index + 1}`}
        >
          Remove
        </button>
      )}
    </div>
  )
}

/**
 * Field — reusable labelled input for the review form.
 */
function Field({ id, label, value, error, onChange, onBlur, placeholder, inputMode, isEdited }) {
  return (
    <div className="field-group">
      <label htmlFor={id} className="flex items-center gap-1 text-xs font-medium text-text-secondary">
        {label}
        {isEdited && (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-400 border border-brand-500/30">
            Edited
          </span>
        )}
      </label>
      <input
        id={id}
        type="text"
        inputMode={inputMode}
        value={value}
        onChange={e => onChange(e.target.value)}
        onBlur={onBlur}
        placeholder={placeholder}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        className={[
          'input',
          error && 'input-error',
        ].join(' ')}
      />
      {error && (
        <p id={`${id}-error`} role="alert" className="field-error">
          {error}
        </p>
      )}
    </div>
  )
}