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
    <div className="rounded-2xl bg-gray-900 border border-gray-800 overflow-hidden">
      {/* Invoice header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-widest">Invoice</p>
          <p className="font-bold text-white text-lg">{invoice.id}</p>
          <p className="text-xs text-gray-500 mt-0.5">{invoice.date}</p>
        </div>
        <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
          {invoice.status.toUpperCase()}
        </span>
      </div>

      {/* Raw input echo */}
      <div className="px-5 py-3 bg-gray-800/40 border-b border-gray-800">
        <p className="text-xs text-gray-500 mb-1">Original input</p>
        <p className="text-sm text-gray-300 italic">"{invoice.rawText}"</p>
      </div>

      {/* Line items table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-xs text-gray-500 uppercase tracking-widest border-b border-gray-800">
              <th className="text-left px-5 py-3 font-medium">Item</th>
              <th className="text-right px-3 py-3 font-medium">Qty</th>
              <th className="text-right px-3 py-3 font-medium">Rate</th>
              <th className="text-right px-3 py-3 font-medium">GST</th>
              <th className="text-right px-5 py-3 font-medium">Total</th>
            </tr>
          </thead>
          <tbody>
            {lines.map((line, i) => (
              <tr key={i} className="border-b border-gray-800/60 hover:bg-gray-800/30 transition">
                <td className="px-5 py-3 text-gray-200">{line.description}</td>
                <td className="px-3 py-3 text-right text-gray-400">{line.qty} {line.unit}</td>
                <td className="px-3 py-3 text-right text-gray-400">{fmt(line.rate)}</td>
                <td className="px-3 py-3 text-right text-gray-400">{line.gstPct}%</td>
                <td className="px-5 py-3 text-right text-gray-200 font-medium">{fmt(line.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Totals */}
      <div className="px-5 py-4 border-t border-gray-800 flex flex-col items-end gap-1">
        <div className="flex gap-8 text-sm text-gray-400">
          <span>Subtotal</span>
          <span>{fmt(grandSubtotal)}</span>
        </div>
        <div className="flex gap-8 text-sm text-gray-400">
          <span>GST</span>
          <span>{fmt(grandGst)}</span>
        </div>
        <div className="flex gap-8 text-base font-bold text-white mt-1 pt-2 border-t border-gray-700 w-full justify-end">
          <span>Total</span>
          <span className="text-brand-500">{fmt(grandTotal)}</span>
        </div>
      </div>

      {/* Actions — wired in later milestones */}
      <div className="px-5 py-4 border-t border-gray-800 flex gap-3">
        <button
          disabled
          className="flex-1 py-2 rounded-lg border border-gray-700 text-gray-500 text-sm font-medium
                     cursor-not-allowed opacity-50"
        >
          Edit Items
        </button>
        <button
          disabled
          className="flex-1 py-2 rounded-lg bg-brand-500 text-white text-sm font-medium
                     cursor-not-allowed opacity-50"
        >
          Send UPI Request
        </button>
      </div>
    </div>
  )
}
