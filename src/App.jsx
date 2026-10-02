import React, { useState } from 'react'
import Header from './components/Header.jsx'
import ChatInput from './components/ChatInput.jsx'
import InvoicePreview from './components/InvoicePreview.jsx'
import EmptyState from './components/EmptyState.jsx'

export default function App() {
  const [invoice, setInvoice] = useState(null)

  return (
    <div className="min-h-screen flex flex-col bg-gray-950">
      <Header />

      <main className="flex-1 flex flex-col lg:flex-row gap-6 p-4 md:p-6 max-w-7xl mx-auto w-full">
        {/* Left: Chat input panel */}
        <section className="flex flex-col gap-4 lg:w-1/2">
          <div className="rounded-2xl bg-gray-900 border border-gray-800 p-5 flex flex-col gap-3">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">
              Order Input
            </h2>
            <p className="text-xs text-gray-500">
              Type your order naturally — like a WhatsApp message. INVOX will extract the items, quantities and GST automatically.
            </p>
            <ChatInput onInvoiceGenerated={setInvoice} />
          </div>
        </section>

        {/* Right: Invoice preview panel */}
        <section className="lg:w-1/2">
          {invoice ? (
            <InvoicePreview invoice={invoice} />
          ) : (
            <EmptyState />
          )}
        </section>
      </main>
    </div>
  )
}
