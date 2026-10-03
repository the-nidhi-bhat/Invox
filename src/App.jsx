import React, { useState, useEffect } from 'react'
import Header from './components/Header.jsx'
import OrderComposer from './components/OrderComposer.jsx'
import LoadingState from './components/LoadingState.jsx'
import ExtractionReview from './components/ExtractionReview.jsx'
import EmptyState from './components/EmptyState.jsx'
import LandingPage from './components/LandingPage.jsx'
import { useTheme } from './context/ThemeContext.jsx'

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

  async function handleGenerateInvoice() {
    if (!gstResult || !confirmedOrder) {
      setInvoiceError('Missing GST calculation or confirmed order')
      setUiState('error')
      return
    }

    setUiState('generating')
    setInvoiceError('')

    try {
      const response = await fetch('/invoice/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_name: confirmedOrder.customer,
          customer_location: confirmedOrder.location,
          items: confirmedOrder.items,
          stated_gst_rate: confirmedOrder.statedGstRate,
          gst_calculation: gstResult,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error ?? 'Invoice generation failed')
      }

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
      const response = await fetch('/upi/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          invoice_number: invoice.invoiceNumber,
          invoice_amount: invoice.grandTotal,
          customer_name: invoice.customer?.name,
          customer_location: invoice.customer?.location,
          customer_vpa: undefined,
          merchant_name: undefined,
          merchant_vpa: undefined,
          transaction_note: undefined,
          currency: 'INR',
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error ?? 'UPI generation failed')
      }

      setUpi(data)
      setUiState('upi')
    } catch (err) {
      setUpiError(err?.message ?? 'UPI generation failed. Please try again.')
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
    setInvoice(null)
    setInvoiceError('')
    setUpi(null)
    setUpiError('')
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
          <div className="card border-status-warning/40 p-8 flex flex-col items-center gap-4 text-center">
            <div className="w-12 h-12 rounded-full bg-status-warning/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-status-warning animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            </div>
            <div>
              <h3 className="text-text-primary font-semibold text-sm">Calculating GST</h3>
              <p className="text-text-muted text-xs mt-1 max-w-[280px]">
                Applying deterministic tax rules…
              </p>
            </div>
          </div>
        )
      case 'confirmed':
        return (
          <div className="flex flex-col gap-4">
            {gstResult?.gst_mismatch && (
              <div className="card border-status-warning/30 p-4 flex items-start gap-3">
                <svg className="w-5 h-5 text-status-warning mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
                <div className="flex-1">
                  <p className="text-xs font-semibold text-status-warning">GST rate mismatch</p>
                  <p className="text-xs text-status-warning/70 mt-1">
                    Message stated <span className="font-semibold font-mono">{gstResult.stated_gst_rate ?? 'no'}%</span> GST,
                    but deterministic rules determine <span className="font-semibold font-mono">{gstResult.determined_gst_rate}%</span>.
                    Calculation uses the <span className="font-semibold">determined rate</span>.
                  </p>
                </div>
              </div>
            )}

            <div className="card p-5 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-text-primary font-semibold text-sm">GST Calculation Complete</h3>
                  <p className="text-text-muted text-xs mt-1">
                    Deterministic rules applied. AI proposed. Rules decided.
                  </p>
                </div>
                <span className="badge-info shrink-0">
                  {gstResult?.tax_type === 'intra_state' ? 'Intra-state (CGST+SGST)' : 'Inter-state (IGST)'}
                </span>
              </div>

              <div className="card p-4 flex flex-col gap-3">
                <p className="text-xs text-text-muted font-medium uppercase tracking-widest">Items</p>
                <div className="flex flex-col gap-2">
                  {gstResult?.items?.map((item, idx) => (
                    <div key={idx} className="card p-3 flex flex-col sm:flex-row sm:items-center gap-3">
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

              <div className="card p-4 flex flex-col gap-2">
                <p className="text-xs text-text-muted font-medium uppercase tracking-widest">Totals</p>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                  <dt className="text-text-muted">Subtotal</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_subtotal.toFixed(2)}</dd>
                  <dt className="text-text-muted">Total GST</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_gst_amount.toFixed(2)}</dd>
                  {gstResult?.tax_type === 'intra_state' ? (
                    <>
                      <dt className="text-text-muted">CGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_cgst.toFixed(2)}</dd>
                      <dt className="text-text-muted">SGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_sgst.toFixed(2)}</dd>
                    </>
                  ) : (
                    <>
                      <dt className="text-text-muted">IGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{gstResult?.total_igst.toFixed(2)}</dd>
                    </>
                  )}
                  <dt className="text-text-muted font-semibold">Grand Total</dt>
                  <dd className="text-text-primary font-semibold text-right font-mono tabular-nums">₹{gstResult?.grand_total.toFixed(2)}</dd>
                </dl>
              </div>

              <div className="rounded-lg bg-status-success/10 border border-status-success/30 p-3 text-center">
                <p className="text-xs text-status-success">
                  Calculation uses deterministic rules. AI proposed the extraction; rules decided the tax.
                </p>
              </div>

              <button
                type="button"
                onClick={handleReset}
                className="btn-secondary btn-md"
              >
                Start new order
              </button>
            </div>
          </div>
        )
      case 'generating':
        return (
          <div className="card border-status-warning/40 p-8 flex flex-col items-center gap-4 text-center">
            <div className="w-12 h-12 rounded-full bg-status-warning/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-status-warning animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            </div>
            <div>
              <h3 className="text-text-primary font-semibold text-sm">Generating Invoice</h3>
              <p className="text-text-muted text-xs mt-1 max-w-[280px]">
                Creating invoice from GST calculation…
              </p>
            </div>
          </div>
        )
      case 'invoice':
        return (
          <div className="flex flex-col gap-4">
            {invoice?.gst_mismatch && (
              <div className="card border-status-warning/30 p-4 flex items-start gap-3">
                <svg className="w-5 h-5 text-status-warning mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                </svg>
                <div className="flex-1">
                  <p className="text-xs font-semibold text-status-warning">GST rate mismatch</p>
                  <p className="text-xs text-status-warning/70 mt-1">
                    Message stated <span className="font-semibold font-mono">{invoice.stated_gst_rate ?? 'no'}%</span> GST,
                    but deterministic rules determine <span className="font-semibold font-mono">{invoice.determined_gst_rate}%</span>.
                    Calculation uses the <span className="font-semibold">determined rate</span>.
                  </p>
                </div>
              </div>
            )}

            <div className="card p-5 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-text-primary font-semibold text-sm">Invoice Generated</h3>
                  <p className="text-text-muted text-xs mt-1">
                    Invoice <span className="font-mono">{invoice?.invoice_number}</span> created on {invoice?.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString('en-IN') : ''}
                  </p>
                </div>
                <span className="badge-info shrink-0">
                  {invoice?.tax_type === 'intra_state' ? 'Intra-state (CGST+SGST)' : 'Inter-state (IGST)'}
                </span>
              </div>

              <div className="card p-4 flex flex-col gap-3">
                <p className="text-xs text-text-muted font-medium uppercase tracking-widest">Seller</p>
                <div className="flex flex-col gap-1 text-xs text-text-muted">
                  <div className="font-medium text-text-primary">{invoice?.seller?.name}</div>
                  <div>{invoice?.seller?.address}</div>
                  <div>State: {invoice?.seller?.state}</div>
                  <div>{invoice?.seller?.gstin}</div>
                </div>
              </div>

              {invoice?.customer?.name && (
                <div className="card p-4 flex flex-col gap-3">
                  <p className="text-xs text-text-muted font-medium uppercase tracking-widest">Customer</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-text-primary">{invoice.customer.name}</span>
                  </div>
                  {invoice.customer.location && (
                    <div className="text-xs text-text-muted">Location: {invoice.customer.location}</div>
                  )}
                </div>
              )}

              <div className="card p-4 flex flex-col gap-3">
                <p className="text-xs text-text-muted font-medium uppercase tracking-widest">Items</p>
                <div className="flex flex-col gap-2">
                  {invoice?.items?.map((item, idx) => (
                    <div key={idx} className="card p-3 flex flex-col sm:flex-row sm:items-center gap-3">
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

              <div className="card p-4 flex flex-col gap-2">
                <p className="text-xs text-text-muted font-medium uppercase tracking-widest">Totals</p>
                <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                  <dt className="text-text-muted">Subtotal</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.subtotal?.toFixed(2)}</dd>
                  <dt className="text-text-muted">Total GST</dt>
                  <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_gst_amount?.toFixed(2)}</dd>
                  {invoice?.tax_type === 'intra_state' ? (
                    <>
                      <dt className="text-text-muted">CGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_cgst?.toFixed(2)}</dd>
                      <dt className="text-text-muted">SGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_sgst?.toFixed(2)}</dd>
                    </>
                  ) : (
                    <>
                      <dt className="text-text-muted">IGST</dt>
                      <dd className="text-text-primary text-right font-mono tabular-nums">₹{invoice?.total_igst?.toFixed(2)}</dd>
                    </>
                  )}
                  <dt className="text-text-muted font-semibold">Grand Total</dt>
                  <dd className="text-text-primary font-semibold text-right font-mono tabular-nums">₹{invoice?.grand_total?.toFixed(2)}</dd>
                </dl>
              </div>

              {invoice?.gst_mismatch && (
                <div className="card border-status-warning/30 p-3 text-center">
                  <p className="text-xs text-status-warning">
                    GST rate mismatch: stated <span className="font-mono">{invoice.stated_gst_rate}%</span> → applied <span className="font-mono">{invoice.determined_gst_rate}%</span>
                  </p>
                </div>
              )}

              <div className="rounded-lg bg-status-success/10 border border-status-success/30 p-3 text-center">
                <p className="text-xs text-status-success">
                  Calculation uses deterministic rules. AI proposed the extraction; rules decided the tax.
                </p>
              </div>

              <div className="flex gap-3">
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
            {upi?.upi_deep_link && (
              <div className="card p-5 flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-text-primary font-semibold text-sm">UPI Payment Request Ready</h3>
                    <p className="text-text-secondary text-xs mt-1">
                      Share this with the customer to complete payment
                    </p>
                  </div>
                  <span className="badge-info shrink-0">
                    UPI Ready
                  </span>
                </div>

                <div className="card p-4 flex flex-col gap-3">
                  <p className="text-xs text-text-muted font-medium uppercase tracking-widest">UPI Deep Link</p>
                  <div className="card p-3 text-center">
                    <code className="text-xs text-brand-500 break-all">{upi.upi_deep_link}</code>
                  </div>
                  <p className="text-xs text-text-muted text-center">
                    Copy this link to share via WhatsApp, SMS, or email
                  </p>
                </div>

                <div className="card p-4 flex flex-col gap-3">
                  <p className="text-xs text-text-muted font-medium uppercase tracking-widest">QR Code</p>
                  <div className="flex justify-center">
                    <img src={upi.qr_code_data} alt="UPI QR Code" className="w-48 h-48" />
                  </div>
                  <p className="text-xs text-text-muted text-center">
                    Scan with any UPI app (PhonePe, GPay, Paytm, etc.)
                  </p>
                </div>

                <div className="card p-4 flex flex-col gap-3">
                  <p className="text-xs text-text-muted font-medium uppercase tracking-widest">Payment Details</p>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                    <dt className="text-text-muted">Amount</dt>
                    <dd className="text-text-primary text-right font-mono">₹{upi?.amount?.toFixed(2)}</dd>
                    <dt className="text-text-muted">Merchant</dt>
                    <dd className="text-text-primary text-right">{upi?.merchant_name}</dd>
                    <dt className="text-text-muted">Merchant VPA</dt>
                    <dd className="text-text-primary text-right font-mono text-xs">{upi?.merchant_vpa}</dd>
                    <dt className="text-text-muted">Status</dt>
                    <dd className="text-text-primary text-right">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-status-warning/10 text-status-warning text-xs border border-status-warning/20">
                        <span className="w-1.5 h-1.5 rounded-full bg-status-warning"></span>
                        {upi?.status === 'pending' ? 'Awaiting Payment' : upi?.status}
                      </span>
                    </dd>
                    <dt className="text-text-muted">Expires</dt>
                    <dd className="text-text-primary text-right">{upi?.expires_at ? new Date(upi.expires_at).toLocaleTimeString('en-IN') : ''}</dd>
                  </dl>
                </div>

                <div className="rounded-lg bg-status-success/10 border border-status-success/30 p-3 text-center">
                  <p className="text-xs text-status-success">
                    UPI deep link and QR code generated. No real payment processed — demo mode only.
                  </p>
                </div>

                <div className="flex gap-3">
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
        return (
          <div className="card border-status-error/40 p-8 flex flex-col items-center gap-4 text-center">
            <div className="w-12 h-12 rounded-full bg-status-error/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-status-error" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div>
              <h3 className="text-text-primary font-semibold text-sm">
                {invoiceError ? 'Invoice generation failed' : gstError ? 'GST calculation failed' : 'Could not process order'}
              </h3>
              <p className="text-text-muted text-xs mt-1 max-w-[280px] leading-relaxed">
                {invoiceError || gstError || extractionError}
              </p>
            </div>
            <button
              type="button"
              onClick={handleReset}
              className="btn-ghost btn-sm"
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
    <div className={`min-h-screen flex flex-col ${theme === 'dark' ? 'dark' : ''} bg-surface`}>
      <Header onEnterApp={handleEnterApp} />

      {uiState === 'landing' ? (
        <LandingPage onEnterApp={handleEnterApp} />
      ) : (
        <main className="flex-1 flex flex-col lg:flex-row gap-6 p-4 md:p-6 max-w-7xl mx-auto w-full">
          {/* Left panel — Order input */}
          <section className="flex flex-col gap-4 lg:w-1/2" aria-label="Order input">
            <div className="card p-5 flex flex-col gap-3">
              <div>
                <h2 className="text-sm font-semibold text-text-primary">
                  New order
                </h2>
                <p className="text-xs text-text-muted mt-1 leading-relaxed">
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
      )}
    </div>
  )
}

/**
 * WorkflowSteps — lightweight visual progress indicator.
 * Shows the seller where they are in the order→invoice→UPI flow.
 * States: idle → loading → review → calculating → confirmed → generating → invoice → upi
 */
function WorkflowSteps({ currentState }) {
  const steps = [
    { id: 'idle',        label: 'Order' },
    { id: 'loading',     label: 'Extract' },
    { id: 'review',      label: 'Review' },
    { id: 'calculating', label: 'GST' },
    { id: 'confirmed',   label: 'Confirm' },
    { id: 'generating',  label: 'Invoice' },
    { id: 'invoice',     label: 'UPI' },
    { id: 'upi',         label: 'Done' },
  ]

  // Map error state to show progress up to review
  const stateMap = {
    'error': 'review',
  }

  const displayState = stateMap[currentState] || currentState
  const activeIndex = steps.findIndex(s => s.id === displayState)

  return (
    <div className="flex items-center gap-0 mt-4" aria-label="Workflow progress" role="list">
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
                          'bg-surface-overlay border border-border text-text-muted',
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
                'text-xs transition hidden sm:inline',
                active ? 'text-text-primary font-medium' : done ? 'text-text-secondary' : 'text-text-muted',
              ].join(' ')}>
                {step.label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={[
                'flex-1 h-px mx-1 transition hidden sm:block',
                i < activeIndex ? 'bg-brand-500/40' : 'bg-border',
              ].join(' ')} aria-hidden="true" />
            )}
          </React.Fragment>
        )
      })}
    </div>
  )
}
