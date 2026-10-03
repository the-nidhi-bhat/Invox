import React from 'react'

/**
 * LandingPage — Product landing page shown before the invoicing workflow.
 * Provides a professional entry point with clear value proposition and CTA.
 */
export default function LandingPage({ onEnterApp }) {
  return (
    <div className="flex min-h-[calc(100dvh-4rem)] flex-col bg-surface">
      <main className="flex flex-1 flex-col">
        <section className="px-4 py-10 md:px-6 md:py-16">
          <div className="container grid items-center gap-10 xl:grid-cols-[1.1fr_0.9fr] xl:gap-12">
            <div className="animate-fade-in">
              <p className="mb-4 text-sm font-semibold text-brand-500">Invoicing, from order to payment</p>
              <h1 className="mb-5 max-w-[680px] text-4xl font-bold leading-tight tracking-tight text-text-primary xl:text-[2.5rem]">
                AI-assisted invoicing from messy business messages.
              </h1>
              <p className="mb-7 max-w-lg text-base leading-relaxed text-text-secondary md:text-lg">
                Turn English or Hinglish orders into invoices. Review every detail before GST rules are applied and payment is requested.
              </p>
              <div className="flex flex-col gap-3 sm:flex-row">
                <button
                  onClick={onEnterApp}
                  className="btn-primary btn-lg w-full whitespace-nowrap sm:w-auto"
                >
                  Open workspace
                </button>
                <button
                  onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}
                  className="btn-secondary btn-lg w-full whitespace-nowrap sm:w-auto"
                >
                  See the workflow
                </button>
              </div>
            </div>

            <div className="animate-slide-up">
              <div className="card overflow-hidden">
                <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
                  <div>
                    <p className="text-xs font-medium text-text-muted">Sample invoice</p>
                    <p className="font-mono text-lg font-bold text-text-primary">INV-20240115-0001</p>
                    <p className="mt-0.5 text-xs text-text-muted">15 Jan 2024</p>
                  </div>
                  <span className="badge-neutral">Draft</span>
                </div>
                <div className="px-5 py-4">
                  <div className="flex items-start justify-between gap-4 border-b border-border-muted pb-4">
                    <div className="min-w-0">
                      <p className="font-medium text-text-primary">Mouse</p>
                      <p className="mt-1 text-xs text-text-muted">50 units at ₹450.00 each</p>
                      <p className="mt-1 text-xs text-text-muted">GST 18%</p>
                    </div>
                    <p className="shrink-0 font-mono text-sm font-medium tabular-nums text-text-primary">₹26,550.00</p>
                  </div>
                  <div className="ml-auto flex max-w-xs flex-col gap-2 pt-4 text-sm">
                    <div className="flex justify-between gap-6 text-text-secondary">
                      <span>Subtotal</span>
                      <span className="font-mono tabular-nums">₹22,500.00</span>
                    </div>
                    <div className="flex justify-between gap-6 text-text-secondary">
                      <span>GST</span>
                      <span className="font-mono tabular-nums">₹4,050.00</span>
                    </div>
                    <div className="mt-1 flex justify-between gap-6 border-t border-border pt-3 font-semibold text-text-primary">
                      <span>Total</span>
                      <span className="font-mono tabular-nums text-brand-500">₹26,550.00</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <ol className="container mt-10 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-6" aria-label="Invoice workflow">
            {['Order message', 'AI extraction', 'Your review', 'GST rules', 'Invoice', 'Payment'].map((step, index) => (
              <li key={step} className="flex min-w-0 items-center gap-2 text-xs font-medium text-text-secondary">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-border bg-surface-elevated font-mono text-[11px] text-brand-500">
                  {index + 1}
                </span>
                <span className="leading-tight">{step}</span>
              </li>
            ))}
          </ol>
        </section>

        {/* Product Principle */}
        <section id="principle" className="py-12 px-4 md:px-6 bg-surface-elevated/30">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-500/10 text-brand-500 border border-brand-500/20 mb-4">
              <span className="text-xs font-semibold uppercase tracking-wider">Core Principle</span>
            </div>
            <h2 className="text-h3 font-bold text-text-primary mb-3">
              AI proposes. Rules decide. You stay in control.
            </h2>
            <p className="text-body text-text-secondary max-w-2xl mx-auto">
              AI extracts intent from messy messages. Deterministic rules calculate GST and totals. You review, edit, and approve before anything moves forward.
            </p>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-14 md:py-20 px-4 md:px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-h3 font-bold text-text-primary mb-3">How it works</h2>
              <p className="text-body text-text-secondary max-w-2xl mx-auto">
                From the first message through invoice creation and payment request.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 md:grid-cols-4 md:gap-6">
              <StepCard
                number="01"
                title="Message"
                description="Type or paste your order naturally in English or Hinglish."
                icon={<MessageIcon />}
              />
              <StepCard
                number="02"
                title="Review"
                description="AI extracts the order. Review and edit every field before continuing."
                icon={<ReviewIcon />}
              />
              <StepCard
                number="03"
                title="GST Validation"
                description="GST rules determine the applicable rate. Any mismatch is shown clearly."
                icon={<GstIcon />}
              />
              <StepCard
                number="04"
                title="Invoice + UPI"
                description="Create a professional invoice and a UPI payment request with a QR code."
                icon={<UpiIcon />}
              />
            </div>
          </div>
        </section>

        {/* Trust / Engineering Principles - concise */}
        <section className="py-14 md:py-20 px-4 md:px-6 bg-surface-elevated/30">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-h3 font-bold text-text-primary mb-3">Built for trust</h2>
              <p className="text-body text-text-secondary max-w-2xl mx-auto">
                Engineering choices that put you in control of every rupee
              </p>
            </div>

            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              <PrincipleCard
                icon={<HumanIcon />}
                title="Human review first"
                description="Nothing ships without your explicit confirmation. Every extracted field is editable."
              />
              <PrincipleCard
                icon={<ShieldIcon />}
                title="Deterministic GST"
                description="AI never calculates tax. Rules engine applies correct rates by category and jurisdiction."
              />
              <PrincipleCard
                icon={<ServerIcon />}
                title="Server-side authority"
                description="Totals calculated on the backend. Client and AI outputs are never trusted for financials."
              />
              <PrincipleCard
                icon={<EyeIcon />}
                title="GST transparency"
                description="Stated vs. rule-derived rates shown side-by-side. Mismatches visibly flagged."
              />
              <PrincipleCard
                icon={<LockIcon />}
                title="No fake payments"
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