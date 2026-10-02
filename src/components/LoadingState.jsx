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
    <div className="rounded-2xl bg-gray-900 border border-gray-800 p-8 flex flex-col gap-5">
      {/* Original message echo */}
      {message && (
        <div className="bg-gray-800/60 rounded-xl px-4 py-3">
          <p className="text-xs text-gray-500 mb-1">Your order</p>
          <p className="text-sm text-gray-300 italic leading-relaxed">"{message}"</p>
        </div>
      )}

      {/* Spinner + status */}
      <div className="flex flex-col items-center gap-4 py-6">
        <div className="relative w-12 h-12" aria-hidden="true">
          <div className="absolute inset-0 rounded-full border-2 border-gray-700" />
          <div className="absolute inset-0 rounded-full border-2 border-t-brand-500 animate-spin" />
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-gray-300">Preparing order details…</p>
          <p className="text-xs text-gray-600 mt-1">Structuring your message</p>
        </div>
      </div>
    </div>
  )
}
