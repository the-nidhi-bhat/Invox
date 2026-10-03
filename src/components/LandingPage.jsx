import React, { useState } from 'react'

/**
 * LandingPage — Product landing page shown before the invoicing workflow.
 * Provides a professional entry point with clear value proposition and CTA.
 */
export default function LandingPage({ onEnterApp }) {
  return (
    <div className="min-h-screen flex flex-col bg-surface">
      <Header onEnterApp={onEnterApp} />
      <main className="flex-1 flex flex-col">
        {/* Hero Section */}
        <section className="relative py-16 md:py-24 px-4 md:px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="animate-fade-in">
              <h1 className="text-h1 font-bold text-text-primary tracking-tight mb-6">
                Turn messy business messages into ready-to-review invoices
              </h1>
              <p className="text-body-lg text-text-secondary max-w-2xl mx-auto mb-10">
                Type orders naturally in English or Hinglish. INVOX extracts the details, you review and confirm, deterministic GST does the math.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <button
                  onClick={onEnterApp}
                  className="btn-primary btn-lg w-full sm:w-auto"
                >
                  Try INVOX
                </button>
                <button
                  onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                  className="btn-secondary btn-lg w-full sm:w-auto"
                >
                  See how it works
                </button>
              </div>
            </div>

            {/* Small product preview */}
            <div className="mt-16 animate-slide-up">
              <div className="card overflow-hidden max-w-3xl mx-auto">
                <div className="flex items-center justify-between px-5 py-4 border-b border-border">
                  <div>
                    <p className="text-xs text-text-muted uppercase tracking-widest">Invoice</p>
                    <p className="font-bold text-text-primary text-lg">INV-20240115-0001</p>
                    <p className="text-xs text-text-muted mt-0.5">15 Jan 2024</p>
                  </div>
                  <span className="badge-warning">Pending</span>
                </div>
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
                        <tr className="border-b border-border/60 hover:bg-surface-overlay/30 transition">
                          <td className="px-5 py-3 text-text-primary">Mouse</td>
                          <td className="px-3 py-3 text-right text-text-muted">50</td>
                          <td className="px-3 py-3 text-right text-text-muted">₹450.00</td>
                          <td className="px-3 py-3 text-right text-text-muted">18%</td>
                          <td className="px-5 py-3 text-right text-text-primary font-medium">₹26,550.00</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div className="px-5 py-4 border-t border-border flex flex-col items-end gap-1">
                    <div className="flex gap-8 text-sm text-text-muted">
                      <span>Subtotal</span>
                      <span>₹22,500.00</span>
                    </div>
                    <div className="flex gap-8 text-sm text-text-muted">
                      <span>GST</span>
                      <span>₹4,050.00</span>
                    </div>
                    <div className="flex gap-8 text-base font-bold text-text-primary mt-1 pt-2 border-t border-border w-full justify-end">
                      <span>Total</span>
                      <span className="text-brand-500">₹26,550.00</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        </section>

        {/* Product Principle */}
        <section id="principle" className="py-16 px-4 md:px-6 bg-surface-elevated/30">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-brand-500/10 text-brand-500 border border-brand-500/20 mb-6">
              <span className="text-xs font-semibold uppercase tracking-wider">Core Principle</span>
            </div>
            <h2 className="text-h2 font-bold text-text-primary mb-4">
              AI proposes. Rules decide. You stay in control.
            </h2>
            <p className="text-body-lg text-text-secondary max-w-2xl mx-auto">
              AI extracts intent from messy messages. Deterministic rules calculate GST and totals. You review, edit, and approve — nothing ships without your sign-off.
            </p>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-16 md:py-24 px-4 md:px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-h2 font-bold text-text-primary mb-4">How it works</h2>
              <p className="text-body-lg text-text-secondary max-w-2xl mx-auto">
                Four steps from messy message to payment request
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 md:gap-8">
              <StepCard
                number="01"
                title="Message"
                description="Type or paste your order naturally — English, Hinglish, abbreviations, any format."
                icon={<MessageIcon />}
              />
              <StepCard
                number="02"
                title="Review"
                description="AI extracts structured data. You review, edit, and confirm every field before proceeding."
                icon={<ReviewIcon />}
              />
              <StepCard
                number="03"
                title="GST Validation"
                description="Deterministic engine applies correct GST rates. Mismatches are flagged, rules decide."
                icon={<GstIcon />}
              />
              <StepCard
                number="04"
                title="Invoice + UPI"
                description="Professional invoice generated. UPI deep link and QR code created for instant payment request."
                icon={<UpiIcon />}
              />
            </div>
          </div>
        </section>

        {/* Trust / Engineering Principles */}
        <section className="py-16 md:py-24 px-4 md:px-6 bg-surface-elevated/30">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-h2 font-bold text-text-primary mb-4">Built for trust</h2>
              <p className="text-body-lg text-text-secondary max-w-2xl mx-auto">
                Engineering choices that put you in control of every rupee
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <PrincipleCard
                icon={<HumanIcon />}
                title="Human review before invoice"
                description="Nothing ships without your explicit confirmation. Every extracted field is editable."
              />
              <PrincipleCard
                icon={<ShieldIcon />}
                title="Deterministic GST calculations"
                description="AI never calculates tax. Rules engine applies correct rates by category and jurisdiction."
              />
              <PrincipleCard
                icon={<ServerIcon />}
                title="Server-side financial authority"
                description="Totals calculated on the backend. Client and AI outputs are never trusted for financials."
              />
              <PrincipleCard
                icon={<EyeIcon />}
                title="GST transparency"
                description="Stated vs. rule-derived rates shown side-by-side. Mismatches visibly flagged."
              />
              <PrincipleCard
                icon={<LockIcon />}
                title="No fake payment integration"
                description="UPI deep links and QR codes only. No payment gateway pretending to process real money."
              />
              <PrincipleCard
                icon={<DatabaseIcon />}
                title="Audit-ready persistence"
                description="Invoices and UPI requests persisted to DynamoDB with idempotency protection."
              />
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-16 md:py-24 px-4 md:px-6">
          <div className="max-w-xl mx-auto text-center">
            <h2 className="text-h2 font-bold text-text-primary mb-6">Ready to create your first invoice?</h2>
            <p className="text-body-lg text-text-secondary mb-10">
              No signup required. No credit card. Just type your order and go.
            </p>
            <button
              onClick={onEnterApp}
              className="btn-primary btn-lg"
            >
              Create an invoice
            </button>
          </div>
        </section>

        <Footer />
      </main>
    </div>
  )
}

// --- Sub-components ---

function Header({ onEnterApp }) {
  return (
    <header className="border-b border-border bg-surface/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 md:px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-brand-500 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-bold text-lg tracking-tight text-text-primary">INVOX</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onEnterApp}
            className="btn-primary btn-sm hidden sm:inline-flex"
          >
            Create invoice
          </button>
        </div>
      </div>
    </header>
  )
}

function StepCard({ number, title, description, icon }) {
  return (
    <div className="card p-6 flex flex-col">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl font-bold text-brand-500/20 font-mono">{number}</span>
        <div className="w-10 h-10 rounded-lg bg-brand-500/10 flex items-center justify-center text-brand-500">
          {icon}
        </div>
      </div>
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-text-muted text-sm leading-relaxed">{description}</p>
    </div>
  )
}

function PrincipleCard({ icon, title, description }) {
  return (
    <div className="card p-6">
      <div className="w-10 h-10 rounded-lg bg-brand-500/10 flex items-center justify-center text-brand-500 mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-text-muted text-sm leading-relaxed">{description}</p>
    </div>
  )
}

function Footer() {
  return (
    <footer className="border-t border-border py-8 px-4 md:px-6">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-5 h-5 rounded-lg bg-brand-500 flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="font-bold text-lg tracking-tight text-text-primary">INVOX</span>
        </div>
        <p className="text-xs text-text-muted">
          Built for the CloudBuild AI Virtual Build-a-Thon. Not a payment processor.
        </p>
      </div>
    </footer>
  )
}

// SVG Icons
function MessageIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  )
}

function ReviewIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}

function GstIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.85 1.072A8.98 8.98 0 0122 12a8.98 8.98 0 01-9.85 6.928C2.92 19.6 2.92 14.4 2.92 12a8.98 8.98 0 019.85-6.928C11.92 7.4 12.89 7 14 7z" />
    </svg>
  )
}

function UpiIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
    </svg>
  )
}

function HumanIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  )
}

function ShieldIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  )
}

function ServerIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
    </svg>
  )
}

function EyeIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  )
}

function LockIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm-10 0V8a2 2 0 012-2h12a2 2 0 012 2v6" />
    </svg>
  )
}

function DatabaseIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.657-3.582 3-8 3s-8-1.343-8-3" />
      <path d="M3 12c0 1.657 3.582 3 8 3s8-1.343 8-3" />
    </svg>
  )
}