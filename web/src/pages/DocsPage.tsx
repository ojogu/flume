import { useState } from 'react'
import { 
  BookOpen, 
  Terminal, 
  Webhook, 
  ShieldCheck, 
  Globe, 
  Key, 
  Copy,
  Check
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Navbar } from '@/components/common/Navbar'
import { Footer } from '@/components/common/Footer'
import { cn } from '@/lib/utils'

export function DocsPage() {
  const [activeSection, setActiveSection] = useState('overview')

  const SECTIONS = [
    { id: 'overview', label: 'Overview', icon: BookOpen },
    { id: 'webhooks', label: 'Webhooks', icon: Webhook },
    { id: 'signature', label: 'Signature Verification', icon: ShieldCheck },
    { id: 'utility', label: 'Utility Endpoints', icon: Terminal },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-[var(--background)]">
      <Navbar />
      
      <div className="flex-1 flex flex-col md:flex-row mx-auto max-w-7xl w-full">
        {/* Desktop Sidebar Navigation */}
        <aside className="hidden md:block w-64 border-r border-[var(--border-subtle)] py-12 px-6 sticky top-16 h-[calc(100vh-64px)] overflow-y-auto">
          <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-[0.2em] mb-6">Documentation</p>
          <nav className="space-y-1">
            {SECTIONS.map(section => (
              <button
                key={section.id}
                onClick={() => {
                  setActiveSection(section.id)
                  document.getElementById(section.id)?.scrollIntoView({ behavior: 'smooth' })
                }}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all group text-left",
                  activeSection === section.id 
                    ? "bg-brand/10 text-brand" 
                    : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-subtle)]"
                )}
              >
                <section.icon className={cn("h-4 w-4", activeSection === section.id ? "text-brand" : "text-[var(--text-muted)] group-hover:text-[var(--text-primary)]")} />
                {section.label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 py-12 px-6 md:px-12 lg:px-16">
          <div className="max-w-3xl">
            {/* Overview Section */}
            <section id="overview" className="mb-24 scroll-mt-24">
              <p className="text-label text-brand mb-4">Introduction</p>
              <h1 className="text-display text-4xl sm:text-5xl lg:text-6xl text-[var(--text-primary)] mb-6">
                API Reference
              </h1>
              <p className="text-lg text-[var(--text-secondary)] leading-relaxed mb-8">
                Build high-performance media workflows with Flume. Our API allows you to automate downloads, trimmings, and processing pipelines using a simple JSON-based interface.
              </p>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-12">
                <div className="p-6 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-strong)] transition-colors">
                  <div className="h-10 w-10 rounded-lg bg-brand/10 flex items-center justify-center mb-4">
                    <Key className="h-5 w-5 text-brand" />
                  </div>
                  <h3 className="font-semibold text-[var(--text-primary)] mb-2">Authentication</h3>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    All API requests must include your API key in the <code className="text-brand font-bold">X-API-Key</code> header.
                  </p>
                </div>
                <div className="p-6 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-strong)] transition-colors">
                  <div className="h-10 w-10 rounded-lg bg-brand/10 flex items-center justify-center mb-4">
                    <Globe className="h-5 w-5 text-brand" />
                  </div>
                  <h3 className="font-semibold text-[var(--text-primary)] mb-2">Base URL</h3>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    Our production API is accessible at: <br/>
                    <code className="text-[10px] text-brand font-bold mt-1 block">https://api.flume.dev/v1</code>
                  </p>
                </div>
              </div>
            </section>

            {/* Webhooks Section */}
            <section id="webhooks" className="mb-24 scroll-mt-24">
              <p className="text-label text-brand mb-4">Real-time Events</p>
              <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)] mb-6">
                Webhooks
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed mb-6">
                Webhooks allow your application to receive real-time notifications when events occur in Flume. Instead of polling for job status, Flume can push updates directly to your server.
              </p>

              <h3 className="text-xl font-semibold text-[var(--text-primary)] mt-10 mb-4">The Event Envelope</h3>
              <p className="text-sm text-[var(--text-secondary)] mb-4">All events are sent as a POST request with the following JSON structure:</p>
              <CodeBlock 
                language="json"
                code={`{
  "id": "evt_uuid",
  "type": "job.completed",
  "created_at": "2026-07-09T12:00:00Z",
  "data": {
    "job_id": "uuid",
    "status": "succeeded",
    "source_uri": "https://youtube.com/watch?v=...",
    "source_type": "video",
    "source_metadata": { ... },
    "error": null
  }
}`}
              />

              <h3 className="text-xl font-semibold text-[var(--text-primary)] mt-12 mb-4">Event Types</h3>
              <div className="rounded-xl border border-[var(--border-subtle)] overflow-hidden mb-8">
                <table className="w-full text-sm text-left">
                  <thead className="bg-[var(--bg-subtle)] border-b border-[var(--border-subtle)]">
                    <tr>
                      <th className="px-4 py-3 font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Event</th>
                      <th className="px-4 py-3 font-mono text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--border-subtle)] bg-[var(--bg-card)]">
                    {[
                      { e: 'job.created', d: 'New job record initialized' },
                      { e: 'job.processing', d: 'Worker has started processing' },
                      { e: 'job.completed', d: 'Processing finished successfully' },
                      { e: 'job.failed', d: 'Job execution stopped due to error' },
                      { e: 'step.started', d: 'A specific pipeline operation began' },
                      { e: 'step.failed', d: 'A pipeline operation encountered an error' },
                    ].map(row => (
                      <tr key={row.e}>
                        <td className="px-4 py-3 font-mono text-xs text-brand font-bold">{row.e}</td>
                        <td className="px-4 py-3 text-[var(--text-secondary)] text-xs">{row.d}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Signature Verification Section */}
            <section id="signature" className="mb-24 scroll-mt-24">
              <p className="text-label text-brand mb-4">Security</p>
              <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)] mb-6">
                Verifying Signatures
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed mb-6">
                To ensure that a webhook request came from Flume, you should verify its digital signature. We include an <code className="font-mono text-brand">X-Signature-256</code> header in every request.
              </p>
              
              <div className="p-5 bg-brand/5 border border-brand/20 rounded-xl mb-8">
                <p className="text-xs text-brand font-semibold leading-relaxed">
                  The signature is a HMAC-SHA256 hash of the raw request body, generated using your subscription's unique secret.
                </p>
              </div>

              <h3 className="text-base font-semibold text-[var(--text-primary)] mb-4">Implementation (Python)</h3>
              <CodeBlock 
                language="python"
                code={`import hmac
import hashlib

def verify_signature(secret, body, signature_header):
    # signature_header format: "sha256=<hex_hash>"
    expected = "sha256=" + hmac.new(
        secret.encode(), 
        body, 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature_header)`}
              />
            </section>

            {/* Utility Endpoints Section */}
            <section id="utility" className="mb-24 scroll-mt-24">
              <p className="text-label text-brand mb-4">Utilities</p>
              <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)] mb-6">
                Utility Endpoints
              </h2>
              
              <div className="space-y-12">
                <div className="group p-6 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-strong)] transition-colors">
                  <div className="flex items-center gap-3 mb-4">
                    <Badge className="bg-blue-500 hover:bg-blue-500 text-white font-mono h-5 text-[10px]">GET</Badge>
                    <code className="text-sm font-bold text-[var(--text-primary)]">/v1/platforms</code>
                  </div>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    Returns a list of all media platforms currently supported for downloads and processing. Useful for UI platform selectors.
                  </p>
                </div>

                <div className="group p-6 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-strong)] transition-colors">
                  <div className="flex items-center gap-3 mb-4">
                    <Badge className="bg-green-500 hover:bg-green-500 text-white font-mono h-5 text-[10px]">POST</Badge>
                    <code className="text-sm font-bold text-[var(--text-primary)]">/v1/verify</code>
                  </div>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    Test your <code className="font-mono">X-API-Key</code>. Returns a <code className="font-bold">200 OK</code> if the key is valid and active.
                  </p>
                </div>

                <div className="group p-6 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-strong)] transition-colors">
                  <div className="flex items-center gap-3 mb-4">
                    <Badge className="bg-blue-500 hover:bg-blue-500 text-white font-mono h-5 text-[10px]">GET</Badge>
                    <code className="text-sm font-bold text-[var(--text-primary)]">/v1/events</code>
                  </div>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                    Returns a machine-readable list of all available event types and their current payload schemas.
                  </p>
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>

      <Footer />
    </div>
  )
}

function CodeBlock({ code, language }: { code: string, language: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="relative group rounded-xl bg-[#0F0F12] border border-white/5 overflow-hidden my-6">
      <div className="flex items-center justify-between px-4 py-2 border-b border-white/5 bg-white/5">
        <span className="text-[10px] font-mono font-bold text-white/40 uppercase tracking-widest">{language}</span>
        <button 
          onClick={handleCopy}
          className="text-white/40 hover:text-white transition-colors"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-brand" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>
      <pre className="p-4 text-[13px] font-mono text-white/80 overflow-x-auto leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  )
}
