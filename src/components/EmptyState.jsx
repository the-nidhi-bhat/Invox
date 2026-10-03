import React from 'react'

export default function EmptyState() {
  return (
    <div className="flex h-full min-h-[320px] flex-col items-center justify-center rounded-2xl border border-dashed border-border-strong bg-surface-elevated/60 p-8 text-center sm:p-10">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-surface">
        <svg className="h-6 w-6 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 className="mb-1 text-sm font-semibold text-text-primary">Your order review will appear here</h3>
      <p className="max-w-xs text-sm leading-relaxed text-text-muted">
        Enter an order message to extract its details. You can check and edit everything before GST is calculated.
      </p>
    </div>
  )
}
