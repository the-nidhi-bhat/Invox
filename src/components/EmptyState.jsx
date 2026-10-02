import React from 'react'

export default function EmptyState() {
  return (
    <div className="rounded-2xl bg-gray-900 border border-gray-800 border-dashed flex flex-col
                    items-center justify-center p-12 text-center h-full min-h-[320px]">
      <div className="w-14 h-14 rounded-2xl bg-gray-800 flex items-center justify-center mb-4">
        <svg className="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <h3 className="text-gray-400 font-semibold text-sm mb-1">No invoice yet</h3>
      <p className="text-gray-600 text-xs max-w-[220px]">
        Describe your order on the left and hit <span className="text-gray-500 font-medium">Generate Invoice</span> — Bedrock will do the rest.
      </p>
    </div>
  )
}
