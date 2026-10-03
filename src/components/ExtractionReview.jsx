import React, { useState } from 'react'

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
    customerState: extraction?.state ?? extraction?.customerState ?? '',
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
      if (index !== null) {
        const newItems = [...prev.items]
        newItems[index] = { ...newItems[index], [field]: value }
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

    if (!draft.customerState?.trim()) {
      e.customerState = 'State is required to determine GST treatment'
    }

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
    setErrors(prev => reindexItemFields(prev, index))
    setTouched(prev => reindexItemFields(prev, index))
    setHumanEdited(prev => reindexItemFields(prev, index))
  }

  function handleConfirm() {
    const e = validate()
    if (Object.keys(e).length > 0) {
      setErrors(e)
      const nextTouched = {
        customer: true,
        location: true,
        customerState: true,
        'stated-gst': true,
      }
      draft.items.forEach((_, idx) => {
        for (const field of ['name', 'quantity', 'unitPrice']) {
          nextTouched[`items.${idx}.${field}`] = true
        }
      })
      setTouched(nextTouched)
      return
    }
    // Filter out items with empty names (shouldn't happen due to validation)
    const validItems = draft.items.filter(item => item.name?.trim())
    onConfirm({
      customer: draft.customer.trim(),
      location: draft.location.trim(),
      customerState: draft.customerState.trim(),
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
      <div className="rounded-xl border border-border-muted bg-surface px-4 py-3">
        <p className="mb-1 text-xs font-medium text-text-muted">Original message</p>
        <p className="break-words text-sm italic leading-relaxed text-text-secondary">“{originalMessage}”</p>
      </div>

      {/* Review card */}
      <div className="card overflow-hidden">

        {/* Card header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div className="min-w-0">
            <h2 className="text-base font-semibold text-text-primary">Review extracted details</h2>
            <p className="mt-1 text-sm text-text-muted">
              AI extracted this information. Nothing is finalized until you confirm.
            </p>
          </div>
          <span className="badge-neutral shrink-0">
            {sourceLabels[source] ?? 'Unknown source'}
          </span>
        </div>

        {/* Notice */}
        <div className="flex items-start gap-2 border-b border-border bg-surface px-5 py-3">
          <svg className="mt-0.5 h-4 w-4 shrink-0 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm leading-relaxed text-text-secondary">
            Check customer, items, and the GST rate stated in the message. Applicable GST is determined in the next step.
          </p>
        </div>

        {/* Fields */}
        <div className="px-5 py-4 flex flex-col gap-4">

          <section aria-labelledby="customer-heading">
            <h3 id="customer-heading" className="mb-3 text-sm font-semibold text-text-primary">Customer</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Field
                id="customer"
                label="Name (optional)"
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
              <Field
                id="customer-state"
                label="State for GST"
                value={draft.customerState}
                error={touched.customerState && errors.customerState}
                onChange={v => updateField('customerState', v)}
                onBlur={() => markTouched('customerState')}
                placeholder="Full state name, e.g. Maharashtra"
                isEdited={humanEdited.customerState}
              />
            </div>
            <p className="mt-2 text-xs leading-relaxed text-text-muted">
              Enter the customer’s state. GST treatment depends on the state, not just the city.
            </p>
          </section>

          <section className="border-t border-border-muted pt-4" aria-labelledby="items-heading">
            <h3 id="items-heading" className="mb-3 text-sm font-semibold text-text-primary">Items</h3>
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
                />
              ))}
              {draft.items.length < 5 && (
                <button
                  type="button"
                  onClick={handleAddItem}
                  className="w-full rounded-lg border border-dashed border-border-strong py-2.5 text-center text-sm font-medium text-brand-500 transition hover:border-brand-500 hover:bg-brand-500/5"
                >
                  + Add another item
                </button>
              )}
            </div>
          </section>

          <section className="border-t border-border-muted pt-4" aria-labelledby="gst-heading">
            <h3 id="gst-heading" className="mb-3 text-sm font-semibold text-text-primary">GST</h3>
            <Field
              id="stated-gst"
              label="Rate stated in the message (optional)"
              value={draft.statedGstRate}
              error={touched['stated-gst'] && errors.statedGstRate}
              onChange={v => updateField('statedGstRate', v)}
              onBlur={() => markTouched('stated-gst')}
              placeholder="For example, 5"
              inputMode="decimal"
              isEdited={humanEdited.statedGstRate}
            />
            <p className="mt-1.5 text-xs leading-relaxed text-text-muted">
              The applicable GST rate is decided by the rules in the next step.
            </p>
          </section>
        </div>

        {/* Actions */}
        <div className="flex flex-col-reverse gap-3 border-t border-border px-5 py-4 sm:flex-row sm:justify-end">
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
            Confirm order
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * ItemRow — a single editable item row in the review form.
 */
function ItemRow({ index, item, errors, touched, humanEdited, onUpdate, onBlur, onRemove, canRemove }) {
  return (
    <div className="rounded-xl border border-border-muted bg-surface p-3">
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start">
      <div className="min-w-0 flex-1">
        <Field
          id={`item-name-${index}`}
          label="Product"
          value={item.name}
          error={touched[`items.${index}.name`] && errors[`items.${index}.name`]}
          onChange={v => onUpdate('name', v)}
          onBlur={() => onBlur('name')}
          placeholder="Product or service name"
          isEdited={humanEdited[`items.${index}.name`]}
        />
      </div>
      <div className="grid w-full grid-cols-2 gap-3 sm:w-auto">
        <Field
          id={`quantity-${index}`}
          label="Qty"
          value={item.quantity}
          error={touched[`items.${index}.quantity`] && errors[`items.${index}.quantity`]}
          onChange={v => onUpdate('quantity', v)}
          onBlur={() => onBlur('quantity')}
          placeholder="e.g. 50"
          inputMode="numeric"
          isEdited={humanEdited[`items.${index}.quantity`]}
          inputClassName="font-mono tabular-nums"
        />
        <Field
          id={`unit-price-${index}`}
          label="Unit price (₹)"
          value={item.unitPrice}
          error={touched[`items.${index}.unitPrice`] && errors[`items.${index}.unitPrice`]}
          onChange={v => onUpdate('unitPrice', v)}
          onBlur={() => onBlur('unitPrice')}
          placeholder="e.g. 450"
          inputMode="decimal"
          isEdited={humanEdited[`items.${index}.unitPrice`]}
          inputClassName="font-mono tabular-nums"
        />
      </div>
      {canRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="self-end rounded-lg border border-border px-3 py-2 text-xs text-text-muted transition hover:border-status-error hover:text-status-error"
          aria-label={`Remove item ${index + 1}`}
        >
          Remove
        </button>
      )}
    </div>
    </div>
  )
}

function reindexItemFields(fields, removedIndex) {
  const result = {}
  for (const [key, value] of Object.entries(fields)) {
    const match = /^items\.(\d+)\.(.+)$/.exec(key)
    if (!match) {
      result[key] = value
      continue
    }

    const index = Number(match[1])
    if (index < removedIndex) {
      result[key] = value
    } else if (index > removedIndex) {
      result[`items.${index - 1}.${match[2]}`] = value
    }
  }
  return result
}

/**
 * Field — reusable labelled input for the review form.
 */
function Field({ id, label, value, error, onChange, onBlur, placeholder, inputMode, isEdited, inputClassName }) {
  return (
    <div className="field-group">
      <label htmlFor={id} className="flex items-center gap-1 text-xs font-medium text-text-secondary">
        {label}
        {isEdited && <span className="text-[10px] font-medium text-brand-500">Edited by you</span>}
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
          isEdited && !error && 'border-brand-500/50 bg-brand-500/5',
          inputClassName,
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