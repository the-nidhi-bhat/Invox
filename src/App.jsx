import React, { useState } from 'react'
import Header from './components/Header.jsx'
import OrderComposer from './components/OrderComposer.jsx'
import LoadingState from './components/LoadingState.jsx'
import ExtractionReview from './components/ExtractionReview.jsx'
import EmptyState from './components/EmptyState.jsx'
import LandingPage from './components/LandingPage.jsx'
import { useTheme } from './context/ThemeContext.jsx'
import {
  normalizeGstResponse,
  normalizeInvoiceResponse,
  normalizeUpiResponse,
  postJson,
} from './services/api.js'

/**
 * App — INVOX root component.
 *
 * UI state machine:
 *
 *   'landing'         — landing page
 *   'idle'            — empty state, waiting for input
 *   'loading'         — extraction in progress (mock or future real API)
 *   'review'          — extraction complete, seller reviews/edits extracted fields
 *   'calculating'     — deterministic GST calculation in progress
 *   'confirmed'       — GST calculated, seller sees final breakdown
 *   'generating'      — invoice generation in progress
 *   'invoice'         — invoice generated, shows final invoice
 *   'upi'             — UPI payment request generated
 *   'error'           — extraction or calculation or generation failed
 *
 * M8 adds: invoice → UPI payment request → UPI
 * M10 adds: landing page, theme support
 */
export default function App() {
  const { theme } = useTheme()
  const [uiState, setUiState] = useState('landing')
  const [composerKey, setComposerKey] = useState(0)
  const [submittedMessage, setSubmittedMessage] = useState('')
  const [extraction, setExtraction] = useState(null)
  const [extractionError, setExtractionError] = useState('')
  const [confirmedOrder, setConfirmedOrder] = useState(null)
  const [gstResult, setGstResult] = useState(null)
  const [gstError, setGstError] = useState('')
  const [invoice, setInvoice] = useState(null)
  const [invoiceError, setInvoiceError] = useState('')
  const [upi, setUpi] = useState(null)
  const [upiError, setUpiError] = useState('')

  function handleEnterApp() {
    setUiState('idle')
  }

  function handleExtractionStart() {
    setUiState('loading')
    setExtraction(null)
    setExtractionError('')
    setConfirmedOrder(null)
    setGstResult(null)
    setGstError('')
    setInvoice(null)
    setInvoiceError('')
    setUpi(null)
    setUpiError('')
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
      const data = normalizeGstResponse(await postJson(
        '/gst/calculate',
        {
          customer_state: draft.customerState,
          items: draft.items.map(item => ({
            name: item.name,
            quantity: item.quantity,
            unit_price: item.unitPrice,
            stated_gst_rate: draft.statedGstRate,
          })),
        },
        'GST calculation failed'
      ))

      setGstResult(data)
      setUiState('confirmed')
    } catch (err) {
      setGstError(err?.message ?? 'GST calculation failed. Please try again.')
      setUiState('error')
    }
  }

  async function handleGenerateInvoice() {
    if (!gstResult || !confirmedOrder) {
      setInvoiceError('Missing GST calculation or confirmed order')
      setUiState('error')
      return
    }

    setUiState('generating')
    setInvoiceError('')

    try {
      const data = normalizeInvoiceResponse(await postJson(
        '/invoice/generate',
        {
          customer_name: confirmedOrder.customer,
          customer_location: confirmedOrder.location,
          items: confirmedOrder.items.map(item => ({
            name: item.name,
            quantity: item.quantity,
            unit_price: item.unitPrice,
          })),
          stated_gst_rate: confirmedOrder.statedGstRate,
          gst_calculation: gstResult,
        },
        'Invoice generation failed'
      ))

      setInvoice(data)
      setUiState('invoice')
    } catch (err) {
      setInvoiceError(err?.message ?? 'Invoice generation failed. Please try again.')
      setUiState('error')
    }
  }

  async function handleGenerateUpi() {
    if (!invoice) {
      setUpiError('Missing invoice')
      setUiState('error')
      return
    }

    setUiState('upi')
    setUpiError('')

    try {
      const data = normalizeUpiResponse(await postJson(
        '/upi/generate',
        {
          invoice_number: invoice.invoice_number,
          invoice_amount: invoice.grand_total,
          customer_name: invoice.customer?.name,
          customer_location: invoice.customer?.location,
          currency: 'INR',
        },
        'Payment request generation failed'
      ))

      setUpi(data)
      setUiState('upi')
    } catch (err) {
      setUpiError(err?.message ?? 'UPI generation failed. Please try again.')
      setUiState('error')
    }
  }

  function resetWorkflow(clearComposer) {
    setUiState('idle')
    setSubmittedMessage('')
    setExtraction(null)
    setExtractionError('')
    setConfirmedOrder(null)
    setGstResult(null)
    setGstError('')
    setInvoice(null)
    setInvoiceError('')
    setUpi(null)
    setUpiError('')
    if (clearComposer) setComposerKey(key => key + 1)
  }

  function handleReset() {
    resetWorkflow(true)
  }

  function handleReturnToOrder() {
    resetWorkflow(false)
  }

  function handleRetry() {
    if (gstError && confirmedOrder) {
      return handleConfirm(confirmedOrder)
    }
    if (invoiceError && gstResult && confirmedOrder) {
      return handleGenerateInvoice()
    }
    if (upiError && invoice) {
      return handleGenerateUpi()
    }
    handleReturnToOrder()
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
          <div className="card flex flex-col gap-4 p-6 sm:p-8" role="status" aria-live="polite">
            <div>
              <h3 className="text-base font-semibold text-text-primary">Applying GST rules</h3>
              <p className="mt-1 text-sm text-text-secondary">Calculating the applicable tax and totals.</p>
            </div>
            <div className="flex flex-col gap-3" aria-hidden="true">
              <div className="h-3 w-3/4 animate-pulse rounded bg-surface-overlay" />
              <div className="h-3 w-full animate-pulse rounded bg-surface-overlay" />
              <div className="h-3 w-1/2 animate-pulse rounded bg-surface-overlay" />
            </div>
          </div>
        )
      case 'confirmed':
        return (
          <div className="flex flex-col gap-4">
            {gstResult?.gst_mismatch && (
              <div className="flex items-start gap-3 rounded-xl border border-status-warning/30 bg-status-warning/5 p-4">
                <svg className="w-5 h-5 text-status-warning mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-text-primary">The stated rate differs from the applicable rate</p>
                  <p className="mt-2 text-sm text-text-secondary">
                    Message stated <span className="font-mono font-semibold text-text-primary">{gstResult.stated_gst_rate ?? 'Not stated'}{gstResult.stated_gst_rate != null ? '%' : ''}</span>.
                    {' '}GST rules determine <span className="font-mono font-semibold text-text-primary">{gstResult.determined_gst_rate}%</span>, which is used in this calculation.
                  </p>
                </div>
              </div>
            )}

            <div className="card flex flex-col gap-5 p-5 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-semibold text-text-primary">GST rules applied</h3>
                  <p className="mt-1 text-sm text-text-secondary">
                    AI proposed the extracted details. Tax rules determine the applicable rate.
                  </p>
                </div>
                <span className="badge-info shrink-0">
                  {gstResult?.tax_type === 'intra_state' ? 'Intra-state (CGST+SGST)' : 'Inter-state (IGST)'}
                </span>
              </div>

              <div className="flex flex-col gap-3">
                <h4 className="text-sm font-semibold text-text-primary">Calculated items</h4>
                <div className="divide-y divide-border rounded-xl border border-border-muted bg-surface px-4">
                  {gstResult?.items?.map((item, idx) => (
                    <div key={idx} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary">{item.name}</p>
                        <p className="text-xs text-text-muted font-mono tabular-nums">
                          Qty: {item.quantity} × ₹{item.unit_price.toFixed(2)}
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 text-xs text-right">
                        <div>
                          <p className="text-text-muted">Subtotal</p>
                          <p className="text-text-primary font-mono tabular-nums">₹{item.subtotal.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-text-muted">GST ({item.gst_rate}%)</p>
                          <p className="text-text-primary font-mono tabular-nums">₹{item.gst_amount.toFixed(2)}</p>
                        </div>
                        {item.tax_type === 'intra_state' ? (
                          <>
                            <div>
                              <p className="text-text-muted">CGST ({item.cgst_rate}%)</p>
                              <p className="text-text-primary font-mono tabular-nums">₹{item.cgst_amount.toFixed(2)}</p>
                            </div>
                            <div>
                              <p className="text-text-muted">SGST ({item.sgst_rate}%)</p>
                              <p className="text-text-primary font-mono tabular-nums">₹{item.sgst_amount.toFixed(2)}</p>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="sm:col-span-2">
                              <p className="text-text-muted">IGST ({item.igst_rate}%)</p>
                              <p className="text-text-primary font-mono tabular-nums">₹{item.igst_amount.toFixed(2)}</p>
                            </div>
                            <div className="sm:hidden" />
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border border-border-muted bg-surface p-4 sm:p-5">
                <h4 className="mb-3 text-sm font-semibold text-text-primary">GST summary</h4>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                  <dt className="text-text-secondary">Subtotal</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_subtotal.toFixed(2)}</dd>
                  <dt className="text-text-secondary">Total GST</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_gst_amount.toFixed(2)}</dd>
                  {gstResult?.tax_type === 'intra_state' ? (
                    <>
                      <dt className="text-text-secondary">CGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_cgst.toFixed(2)}</dd>
                      <dt className="text-text-secondary">SGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_sgst.toFixed(2)}</dd>
                    </>
                  ) : (
                    <>
                      <dt className="text-text-secondary">IGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_igst.toFixed(2)}</dd>
                    </>
                  )}
                  <dt className="border-t border-border pt-3 font-semibold text-text-primary">Grand total</dt>
                  <dd className="border-t border-border pt-2 text-right font-mono text-xl font-bold tabular-nums text-brand-500">₹{gstResult?.grand_total.toFixed(2)}</dd>
                </dl>
              </div>

              <div className="rounded-xl border border-status-success/30 bg-status-success/5 p-3">
                <p className="text-sm leading-relaxed text-text-secondary">
                  AI helps organize the order. GST rates and totals are calculated by the rules engine.
                </p>
              </div>

              <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={handleReset}
                  className="btn-secondary btn-md"
                >
                  Start new order
                </button>
                <button
                  type="button"
                  onClick={handleGenerateInvoice}
                  className="btn-primary btn-md"
                >
                  Generate Invoice
                </button>
              </div>
            </div>
          </div>
        )
      case 'generating':
        return (
          <div className="card flex flex-col gap-4 p-6 sm:p-8" role="status" aria-live="polite">
            <div>
              <h3 className="text-base font-semibold text-text-primary">Generating invoice</h3>
              <p className="mt-1 text-sm text-text-secondary">Preparing the invoice from the confirmed GST calculation.</p>
            </div>
            <div className="flex flex-col gap-3" aria-hidden="true">
              <div className="h-3 w-3/4 animate-pulse rounded bg-surface-overlay" />
              <div className="h-3 w-full animate-pulse rounded bg-surface-overlay" />
              <div className="h-3 w-1/2 animate-pulse rounded bg-surface-overlay" />
            </div>
          </div>
        )
      case 'invoice':
        return (
          <div className="flex flex-col gap-4">
            {invoice?.gst_mismatch && (
              <div className="flex items-start gap-3 rounded-xl border border-status-warning/30 bg-status-warning/5 p-4">
                <svg className="w-5 h-5 text-status-warning mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-text-primary">The stated rate differs from the applicable rate</p>
                  <p className="mt-2 text-sm text-text-secondary">
                    Message stated <span className="font-mono font-semibold text-text-primary">{invoice.stated_gst_rate ?? 'Not stated'}{invoice.stated_gst_rate != null ? '%' : ''}</span>.
                    {' '}GST rules determine <span className="font-mono font-semibold text-text-primary">{invoice.determined_gst_rate}%</span>, which is used in this invoice.
                  </p>
                </div>
              </div>
            )}

            <div className="card flex flex-col gap-5 border-border-strong p-5 shadow-md sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-text-primary">Invoice</h3>
                  <p className="mt-1 text-sm text-text-secondary">
                    Invoice <span className="font-mono">{invoice?.invoice_number}</span> created on {invoice?.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString('en-IN') : ''}
                  </p>
                </div>
                <span className="badge-neutral shrink-0">{invoice?.tax_type === 'intra_state' ? 'CGST + SGST' : 'IGST'}</span>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="rounded-xl border border-border-muted bg-surface p-4">
                  <h4 className="mb-2 text-xs font-semibold text-text-muted">From</h4>
                  <div className="flex flex-col gap-1 break-words text-sm text-text-secondary">
                    <div className="font-semibold text-text-primary">{invoice?.seller?.name}</div>
                    <div>{invoice?.seller?.address}</div>
                    <div>{invoice?.seller?.state}</div>
                    <div className="font-mono text-xs">{invoice?.seller?.gstin}</div>
                  </div>
                </div>
                {invoice?.customer?.name && (
                  <div className="rounded-xl border border-border-muted bg-surface p-4">
                    <h4 className="mb-2 text-xs font-semibold text-text-muted">Bill to</h4>
                    <div className="text-sm font-semibold text-text-primary">{invoice.customer.name}</div>
                    {invoice.customer.location && (
                      <div className="mt-1 text-sm text-text-secondary">{invoice.customer.location}</div>
                    )}
                  </div>
                )}
              </div>

              <div className="flex flex-col gap-3">
                <h4 className="text-sm font-semibold text-text-primary">Line items</h4>
                <div className="divide-y divide-border rounded-xl border border-border-muted bg-surface px-4">
                  {invoice?.items?.map((item, idx) => (
                    <div key={idx} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary">{item.name}</p>
                        <p className="text-xs text-text-muted font-mono tabular-nums">
                          Qty: {item.quantity} × ₹{item.unit_price.toFixed(2)}
                        </p>
                      </div>
                      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 text-xs text-right">
                        <div>
                          <p className="text-text-muted">Subtotal</p>
                          <p className="text-text-primary font-mono tabular-nums">₹{item.subtotal.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-text-muted">GST ({item.gst_rate}%)</p>
                          <p className="text-text-primary font-mono tabular-nums">₹{item.gst_amount.toFixed(2)}</p>
                        </div>
                        {item.tax_type === 'intra_state' ? (
                          <>
                            <div>
                              <p className="text-text-muted">CGST ({item.cgst_rate}%)</p>
                              <p className="text-text-primary font-mono tabular-nums">₹{item.cgst_amount.toFixed(2)}</p>
                            </div>
                            <div>
                              <p className="text-text-muted">SGST ({item.sgst_rate}%)</p>
                              <p className="text-text-primary font-mono tabular-nums">₹{item.sgst_amount.toFixed(2)}</p>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="sm:col-span-2">
                              <p className="text-text-muted">IGST ({item.igst_rate}%)</p>
                              <p className="text-text-primary font-mono tabular-nums">₹{item.igst_amount.toFixed(2)}</p>
                            </div>
                            <div className="sm:hidden" />
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border border-border-muted bg-surface p-4 sm:p-5">
                <h4 className="mb-3 text-sm font-semibold text-text-primary">Totals</h4>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                  <dt className="text-text-secondary">Subtotal</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.subtotal?.toFixed(2)}</dd>
                  <dt className="text-text-secondary">Total GST</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_gst_amount?.toFixed(2)}</dd>
                  {invoice?.tax_type === 'intra_state' ? (
                    <>
                      <dt className="text-text-secondary">CGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_cgst?.toFixed(2)}</dd>
                      <dt className="text-text-secondary">SGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_sgst?.toFixed(2)}</dd>
                    </>
                  ) : (
                    <>
                      <dt className="text-text-secondary">IGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_igst?.toFixed(2)}</dd>
                    </>
                  )}
                  <dt className="border-t border-border pt-3 font-semibold text-text-primary">Grand total</dt>
                  <dd className="border-t border-border pt-2 text-right font-mono text-xl font-bold tabular-nums text-brand-500">₹{invoice?.grand_total?.toFixed(2)}</dd>
                </dl>
              </div>

              {invoice?.gst_mismatch && (
                <div className="rounded-lg border border-status-warning/30 bg-status-warning/5 p-3">
                  <p className="text-sm text-text-secondary">
                    GST rate mismatch: stated <span className="font-mono">{invoice.stated_gst_rate}%</span> → applied <span className="font-mono">{invoice.determined_gst_rate}%</span>
                  </p>
                </div>
              )}

              <div className="rounded-xl border border-status-success/30 bg-status-success/5 p-3">
                <p className="text-sm text-text-secondary">
                  AI helps organize the order. GST rates and totals are calculated by the rules engine.
                </p>
              </div>

              <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <button
                  type="button"
                  onClick={handleGenerateUpi}
                  className="btn-primary btn-md"
                >
                  Generate UPI Payment
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="btn-secondary btn-md"
                >
                  Start new order
                </button>
              </div>
            </div>
          </div>
        )
case 'upi':
        return (
          <div className="flex flex-col gap-4">
      {!upi && (
        <div className="card flex flex-col gap-4 p-6 sm:p-8" role="status" aria-live="polite">
          <div>
            <h3 className="text-base font-semibold text-text-primary">Preparing payment request</h3>
            <p className="mt-1 text-sm text-text-secondary">Creating the UPI link and QR code.</p>
          </div>
          <div className="flex flex-col gap-3" aria-hidden="true">
            <div className="h-3 w-3/4 animate-pulse rounded bg-surface-overlay" />
            <div className="h-3 w-full animate-pulse rounded bg-surface-overlay" />
            <div className="h-3 w-1/2 animate-pulse rounded bg-surface-overlay" />
          </div>
        </div>
      )}
      {upi?.upi_deep_link && (
                <div className="card flex flex-col gap-5 p-5 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                      <h3 className="text-lg font-semibold text-text-primary">Payment request</h3>
                      <p className="mt-1 text-sm text-text-secondary">
                        Share the payment link or QR code with your customer.
                    </p>
                  </div>
                    <span className="badge-warning shrink-0">{upi?.status === 'pending' ? 'Pending' : upi?.status}</span>
                  </div>

                  <div className="rounded-xl border border-border-muted bg-surface p-4">
                    <p className="text-xs font-medium text-text-muted">Amount requested</p>
                    <p className="mt-1 font-mono text-3xl font-bold tabular-nums tracking-tight text-text-primary">
                      ₹{upi?.amount?.toFixed(2)}
                    </p>
                    <p className="mt-1 text-sm text-text-secondary">
                      Invoice <span className="font-mono">{invoice?.invoice_number}</span>
                    </p>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="flex min-w-0 flex-col items-start gap-3 rounded-xl border border-border-muted bg-surface p-4">
                      <h4 className="text-sm font-semibold text-text-primary">Pay using UPI</h4>
                      <p className="text-sm leading-relaxed text-text-secondary">
                        Open the payment request in a UPI app on this device.
                      </p>
                      <a href={upi.upi_deep_link} className="btn-primary btn-md mt-auto w-full whitespace-nowrap">
                        Open UPI app
                      </a>
                      <details className="w-full">
                        <summary className="cursor-pointer text-xs font-medium text-text-secondary focus-visible:outline-none">
                          View payment link
                        </summary>
                        <code className="mt-2 block break-all rounded-lg border border-border bg-surface-elevated p-3 text-xs text-brand-500">
                          {upi.upi_deep_link}
                        </code>
                      </details>
                    </div>

                    <div className="flex flex-col items-center gap-3 rounded-xl border border-border-muted bg-surface p-4 text-center">
                      <h4 className="text-sm font-semibold text-text-primary">Scan to pay</h4>
                      <img src={upi.qr_code_data} alt="QR code for this UPI payment request" className="h-40 w-40 rounded-lg bg-white p-2" />
                      <p className="text-xs leading-relaxed text-text-secondary">Scan with a UPI app on another device.</p>
                    </div>
                  </div>

                  <div className="rounded-xl border border-border-muted bg-surface p-4">
                    <h4 className="mb-3 text-sm font-semibold text-text-primary">Request details</h4>
                    <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                      <dt className="text-text-secondary">Merchant</dt>
                      <dd className="break-words text-right text-text-primary">{upi?.merchant_name}</dd>
                      <dt className="text-text-secondary">UPI ID</dt>
                      <dd className="break-all text-right font-mono text-xs text-text-primary">{upi?.merchant_vpa}</dd>
                      <dt className="text-text-secondary">Status</dt>
                      <dd className="text-right"><span className="badge-warning">{upi?.status === 'pending' ? 'Pending' : upi?.status}</span></dd>
                      <dt className="text-text-secondary">Expires</dt>
                      <dd className="text-right text-text-primary">{upi?.expires_at ? new Date(upi.expires_at).toLocaleTimeString('en-IN') : 'Not specified'}</dd>
                    </dl>
                  </div>

                  <div className="rounded-xl border border-status-warning/30 bg-status-warning/5 p-3">
                    <p className="text-sm leading-relaxed text-text-secondary">
                      This request does not verify payment. Confirm receipt separately; INVOX does not receive payment confirmation.
                    </p>
                  </div>

                  <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                  <button
                    type="button"
                    onClick={handleReset}
                    className="btn-secondary btn-md"
                  >
                    Start new order
                  </button>
                  <button
                    type="button"
                    disabled={true}
                    className="btn-ghost btn-md"
                  >
                    Payment Received
                  </button>
                </div>
              </div>
            )}
          </div>
        )
      case 'error':
        const errorTitle = invoiceError
          ? 'Invoice generation failed'
          : gstError
            ? 'GST calculation failed'
            : upiError
              ? 'Payment request failed'
              : 'Could not process order'
        const errorMessage = invoiceError || gstError || upiError || extractionError
        return (
          <div className="card flex flex-col items-start gap-4 border-status-error/40 p-6 sm:p-8" role="alert">
            <div className="w-12 h-12 rounded-full bg-status-error/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-status-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-primary">{errorTitle}</h3>
              <p className="mt-1 max-w-[280px] break-words text-xs leading-relaxed text-text-muted">
                {errorMessage}
              </p>
            </div>
            <div className="flex w-full flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={handleReset}
                className="btn-secondary btn-md"
              >
                Start new order
              </button>
              <button
                type="button"
                onClick={extractionError && !gstError && !invoiceError && !upiError ? handleReturnToOrder : handleRetry}
                className="btn-ghost btn-md"
              >
                {extractionError && !gstError && !invoiceError && !upiError
                  ? 'Return to order'
                  : 'Try again'}
              </button>
            </div>
          </div>
        )
      default: // 'idle'
        return <EmptyState />
    }
  }

  return (
    <div className={`flex min-h-[100dvh] flex-col ${theme === 'dark' ? 'dark' : ''} bg-surface`}>
      <Header />

      {uiState === 'landing' ? (
        <LandingPage onEnterApp={handleEnterApp} />
      ) : (
        <main className="mx-auto grid w-full max-w-7xl flex-1 grid-cols-1 gap-5 px-4 py-6 md:gap-6 md:px-6 md:py-8 lg:grid-cols-2">
          <WorkflowSteps
            currentState={uiState}
            errorStage={gstError ? 'gst' : invoiceError ? 'invoice' : upiError ? 'upi' : 'review'}
          />
          {/* Left panel — Order input */}
          <section className="flex min-w-0 flex-col gap-4" aria-label="Order input">
            <div className="card flex flex-col gap-4 p-5 sm:p-6">
              <div>
                <h2 className="text-lg font-semibold text-text-primary">
                  Start with the order message
                </h2>
                <p className="mt-1 text-sm leading-relaxed text-text-secondary">
                  Paste what your customer sent. INVOX organizes the details for you to check.
                </p>
              </div>
              <OrderComposer
                key={composerKey}
                disabled={uiState === 'calculating' || uiState === 'generating' || (uiState === 'upi' && !upi)}
                onExtractionStart={() => {
                  // Capture the message before it gets cleared
                  handleExtractionStart()
                }}
                onExtractionSuccess={handleExtractionSuccess}
                onExtractionError={handleExtractionError}
              />
            </div>

          </section>

          {/* Right panel — dynamic content */}
          <section className="min-w-0" aria-label="Extraction result and review">
            {renderRightPanel()}
          </section>
        </main>
      )}
    </div>
  )
}

/**
 * WorkflowSteps shows progress through the five customer-facing workflow stages.
 */
function WorkflowSteps({ currentState, errorStage }) {
  const steps = [
    { id: 'idle', label: 'Order' },
    { id: 'review', label: 'Review' },
    { id: 'gst', label: 'GST' },
    { id: 'invoice', label: 'Invoice' },
    { id: 'upi', label: 'Payment' },
  ]

  const stateMap = {
    loading: 'idle',
    calculating: 'gst',
    confirmed: 'gst',
    generating: 'invoice',
    error: errorStage,
  }

  const displayState = stateMap[currentState] || currentState
  const activeIndex = steps.findIndex(s => s.id === displayState)

  return (
    <ol className="col-span-full grid min-w-0 grid-cols-5 gap-1 rounded-xl border border-border bg-surface-elevated px-2 py-3 md:flex md:items-center md:px-5" aria-label="Workflow progress">
      {steps.map((step, i) => {
        const done = i < activeIndex
        const active = i === activeIndex
        return (
          <React.Fragment key={step.id}>
            <li
              className="flex min-w-0 flex-col items-center justify-center gap-1 md:flex-1 md:flex-row md:justify-start md:gap-2"
              aria-current={active ? 'step' : undefined}
              aria-label={`${step.label}: ${done ? 'completed' : active ? 'current step' : 'upcoming'}`}
            >
              <div className={[
                'flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs font-semibold transition-colors',
                done ? 'border-brand-600 bg-brand-600 text-white' :
                active ? 'border-brand-500 bg-brand-500/10 text-brand-500' :
                  'border-border bg-surface text-text-muted',
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
                'min-w-0 text-center text-[9px] leading-tight transition md:text-left md:text-xs',
                active ? 'font-semibold text-text-primary' : done ? 'text-text-secondary' : 'text-text-muted',
              ].join(' ')}>
                {step.label}
              </span>
            </li>
            {i < steps.length - 1 && (
              <div className={[
                'hidden h-px shrink-0 transition-colors md:mx-3 md:block md:w-6 md:flex-none',
                i < activeIndex ? 'bg-brand-500/60' : 'bg-border',
              ].join(' ')} aria-hidden="true" />
            )}
          </React.Fragment>
        )
      })}
    </ol>
  )
}
