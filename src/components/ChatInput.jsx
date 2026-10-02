import React, { useState } from 'react'

const PLACEHOLDER_EXAMPLES = [
  '2 kg onions at ₹40/kg, 5 litres milk at ₹60 each',
  '3 shirts at 799 each, 1 trouser 1499',
  '10 pcs notebook 50 each, 2 pens 15 each',
]

export default function ChatInput({ onInvoiceGenerated }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [placeholder] = useState(
    () => PLACEHOLDER_EXAMPLES[Math.floor(Math.random() * PLACEHOLDER_EXAMPLES.length)]
  )

  async function handleSubmit(e) {
    e.preventDefault()
    if (!text.trim()) return

    setLoading(true)
    // Milestone 3 will wire this to Bedrock via API Gateway.
    // For now, emit a mock invoice so the UI can be verified end-to-end.
    await new Promise(r => setTimeout(r, 800))
    onInvoiceGenerated({
      id: `INV-${Date.now()}`,
      date: new Date().toLocaleDateString('en-IN'),
      rawText: text,
      items: [
        { description: 'Sample Item A', qty: 2, unit: 'pcs', rate: 500, gstPct: 18 },
        { description: 'Sample Item B', qty: 1, unit: 'pcs', rate: 1200, gstPct: 12 },
      ],
      status: 'draft',
    })
    setLoading(false)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <textarea
        className="w-full min-h-[140px] rounded-xl bg-gray-800 border border-gray-700 text-gray-100 text-sm p-4
                   placeholder-gray-600 resize-none focus:outline-none focus:ring-2 focus:ring-brand-500
                   focus:border-transparent transition"
        placeholder={placeholder}
        value={text}
        onChange={e => setText(e.target.value)}
        disabled={loading}
        aria-label="Order description"
      />

      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-600">
          Bedrock AI extracts items · GST applied automatically
        </p>
        <button
          type="submit"
          disabled={!text.trim() || loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-600
                     disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium
                     transition focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2
                     focus:ring-offset-gray-900"
        >
          {loading ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Processing…
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Invoice
            </>
          )}
        </button>
      </div>
    </form>
  )
}
