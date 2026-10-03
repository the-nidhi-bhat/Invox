import React from 'react'

export default function EmptyState() {
  return (
    <div className="card border-dashed flex flex-col items-center justify-center p-10 text-center h-full min-h-[320px]">
      <div className="w-14 h-14 rounded-2xl bg-surface-elevated flex items-center justify-center mb-4">
        <svg className="w-7 h-7 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 className="text-text-secondary font-semibold text-sm mb-1">No order yet</h3>
      <p className="text-text-muted text-xs max-w-[240px] leading-relaxed">
        Type your order on the left and hit{' '}
        <span className="text-text-secondary font-medium">Extract Order</span>{' '}
        to review the extracted details.
      </p>
    </div>
  )
}
