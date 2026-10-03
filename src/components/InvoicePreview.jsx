import React from 'react'

function calcLine(item) {
  const subtotal = item.qty * item.rate
  const gst = (subtotal * item.gstPct) / 100
  return { subtotal, gst, total: subtotal + gst }
}

export default function InvoicePreview({ invoice }) {
  const lines = invoice.items.map(item => ({ ...item, ...calcLine(item) }))
  const grandSubtotal = lines.reduce((s, l) => s + l.subtotal, 0)
  const grandGst = lines.reduce((s, l) => s + l.gst, 0)
  const grandTotal = grandSubtotal + grandGst

  const fmt = n => `₹${n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

  return (
    <article className="overflow-hidden rounded-2xl border border-border-strong bg-surface-elevated shadow-md" aria-label={`Invoice ${invoice.id}`}>
      <header className="flex items-start justify-between gap-4 border-b border-border px-5 py-5 sm:px-7">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-text-secondary">Invoice</p>
          <p className="mt-1 break-all font-mono text-lg font-bold text-text-primary">{invoice.id}</p>
          <p className="mt-1 text-sm text-text-secondary">{invoice.date}</p>
        </div>
        <span className="badge-neutral shrink-0">
          {invoice.status}
        </span>
      </header>

      {(invoice.seller || invoice.customer) && (
        <section className="grid grid-cols-1 gap-4 border-b border-border px-5 py-5 sm:grid-cols-2 sm:px-7">
          {invoice.seller && (
            <div>
              <h3 className="mb-2 text-xs font-semibold text-text-muted">From</h3>
              <p className="text-sm font-semibold text-text-primary">{invoice.seller.name}</p>
              {invoice.seller.address && <p className="mt-1 text-sm text-text-secondary">{invoice.seller.address}</p>}
              {invoice.seller.state && <p className="mt-1 text-sm text-text-secondary">{invoice.seller.state}</p>}
              {invoice.seller.gstin && <p className="mt-1 font-mono text-xs text-text-secondary">{invoice.seller.gstin}</p>}
            </div>
          )}
          {invoice.customer && (
            <div>
              <h3 className="mb-2 text-xs font-semibold text-text-muted">Bill to</h3>
              <p className="text-sm font-semibold text-text-primary">{invoice.customer.name}</p>
              {invoice.customer.location && <p className="mt-1 text-sm text-text-secondary">{invoice.customer.location}</p>}
            </div>
          )}
        </section>
      )}

      <section className="px-5 py-5 sm:px-7" aria-labelledby="invoice-items-heading">
        <h3 id="invoice-items-heading" className="mb-3 text-sm font-semibold text-text-primary">Items</h3>
        <div className="divide-y divide-border border-y border-border-muted">
          {lines.map((line, i) => (
            <div key={i} className="grid grid-cols-[minmax(0,1fr)_auto] gap-4 py-4">
              <div className="min-w-0">
                <p className="break-words text-sm font-medium text-text-primary">{line.description}</p>
                <p className="mt-1 text-xs text-text-secondary">
                  {line.qty} {line.unit} at {fmt(line.rate)} each
                </p>
                <p className="mt-1 text-xs text-text-muted">GST {line.gstPct}% · {fmt(line.gst)}</p>
              </div>
              <p className="whitespace-nowrap text-right font-mono text-sm font-semibold tabular-nums text-text-primary">
                {fmt(line.total)}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="ml-auto flex max-w-sm flex-col gap-2 px-5 pb-5 sm:px-7" aria-label="Invoice totals">
        <div className="flex justify-between gap-6 text-sm text-text-secondary">
          <span>Subtotal</span>
          <span className="font-mono tabular-nums text-text-primary">{fmt(grandSubtotal)}</span>
        </div>
        <div className="flex justify-between gap-6 text-sm text-text-secondary">
          <span>GST</span>
          <span className="font-mono tabular-nums text-text-primary">{fmt(grandGst)}</span>
        </div>
        <div className="mt-1 flex justify-between gap-6 border-t border-border pt-3 text-base font-bold text-text-primary">
          <span>Total</span>
          <span className="font-mono text-xl tabular-nums text-brand-500">{fmt(grandTotal)}</span>
        </div>
      </section>

      <footer className="flex flex-col-reverse gap-3 border-t border-border px-5 py-4 sm:flex-row sm:justify-end sm:px-7">
        <button
          disabled
          className="btn-secondary btn-sm"
        >
          Edit Items
        </button>
        <button
          disabled
          className="btn-primary btn-sm"
        >
          Send UPI Request
        </button>
      </footer>
    </article>
  )
}
