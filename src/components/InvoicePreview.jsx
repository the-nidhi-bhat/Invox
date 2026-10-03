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
    <div className="card overflow-hidden">
      {/* Invoice header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border">
        <div>
          <p className="text-xs text-text-muted uppercase tracking-widest">Invoice</p>
          <p className="font-bold text-text-primary text-lg">{invoice.id}</p>
          <p className="text-xs text-text-muted mt-0.5">{invoice.date}</p>
        </div>
        <span className="badge-warning">
          {invoice.status.toUpperCase()}
        </span>
      </div>

      {/* Raw input echo */}
      <div className="px-5 py-3 bg-surface-overlay/40 border-b border-border">
        <p className="text-xs text-text-muted mb-1">Original input</p>
        <p className="text-sm text-text-secondary italic">"{invoice.rawText}"</p>
      </div>

      {/* Line items table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-text-muted uppercase tracking-widest border-b border-border">
              <th className="text-left px-5 py-3 font-medium">Item</th>
              <th className="text-right px-3 py-3 font-medium">Qty</th>
              <th className="text-right px-3 py-3 font-medium">Rate</th>
              <th className="text-right px-3 py-3 font-medium">GST</th>
              <th className="text-right px-5 py-3 font-medium">Total</th>
            </tr>
          </thead>
          <tbody>
            {lines.map((line, i) => (
              <tr key={i} className="border-b border-border/60 hover:bg-surface-overlay/30 transition">
                <td className="px-5 py-3 text-text-primary">{line.description}</td>
                <td className="px-3 py-3 text-right text-text-muted">{line.qty} {line.unit}</td>
                <td className="px-3 py-3 text-right text-text-muted">{fmt(line.rate)}</td>
                <td className="px-3 py-3 text-right text-text-muted">{line.gstPct}%</td>
                <td className="px-5 py-3 text-right text-text-primary font-medium">{fmt(line.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Totals */}
      <div className="px-5 py-4 border-t border-border flex flex-col items-end gap-1">
        <div className="flex gap-8 text-sm text-text-muted">
          <span>Subtotal</span>
          <span>{fmt(grandSubtotal)}</span>
        </div>
        <div className="flex gap-8 text-sm text-text-muted">
          <span>GST</span>
          <span>{fmt(grandGst)}</span>
        </div>
        <div className="flex gap-8 text-base font-bold text-text-primary mt-1 pt-2 border-t border-border w-full justify-end">
          <span>Total</span>
          <span className="text-brand-500">{fmt(grandTotal)}</span>
        </div>
      </div>

      {/* Actions — wired in later milestones */}
      <div className="px-5 py-4 border-t border-border flex gap-3">
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
      </div>
    </div>
  )
}
