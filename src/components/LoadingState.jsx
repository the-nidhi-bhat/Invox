import React from 'react'

/**
 * LoadingState
 * Shown while the mock extractor (or future real API) is running.
 *
 * Props:
 *   message  — the original order text, shown as context
 */
export default function LoadingState({ message }) {
  return (
    <div className="card flex flex-col gap-5 p-5 sm:p-6" role="status" aria-live="polite">
      {message && (
        <div className="rounded-xl border border-border-muted bg-surface px-4 py-3">
          <p className="mb-1 text-xs font-medium text-text-muted">Order message</p>
          <p className="break-words text-sm italic leading-relaxed text-text-secondary">“{message}”</p>
        </div>
      )}

      <div className="flex flex-col gap-4 py-2">
        <div>
          <p className="text-sm font-semibold text-text-primary">Extracting order details</p>
          <p className="mt-1 text-sm text-text-muted">Organizing the message for your review.</p>
        </div>
        <div className="flex flex-col gap-3" aria-hidden="true">
          <div className="h-3 w-2/3 animate-pulse rounded bg-surface-overlay" />
          <div className="h-3 w-full animate-pulse rounded bg-surface-overlay" />
          <div className="h-3 w-1/2 animate-pulse rounded bg-surface-overlay" />
        </div>
      </div>
    </div>
  )
}
