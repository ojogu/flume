import { useState } from 'react'
import { LoaderCircle, Mail, Send, MessageCircle, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

const V1_BASE = import.meta.env.VITE_API_URL + '/v1'

const SUPPORT_EMAIL = 'support@ojogulabs.xyz'
const SUPPORT_WHATSAPP = 'https://wa.me/2349065011334'

export function SupportPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSent(false)

    try {
      const res = await fetch(`${V1_BASE}/support/contact`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, subject, message }),
      })
      const body = await res.json()
      if (res.ok && body.status === 'success') {
        setSent(true)
        setName('')
        setEmail('')
        setSubject('')
        setMessage('')
      } else {
        setError(body.message || 'Something went wrong. Please try again.')
      }
    } catch {
      setError('Failed to connect to the server. Please check your connection or reach us directly.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-display text-3xl text-[var(--text-primary)]">Support</h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          We usually respond within one business day.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 lg:col-span-2">
          {sent ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <CheckCircle2 className="h-12 w-12 text-brand mb-4" />
              <h2 className="text-display text-xl text-[var(--text-primary)] mb-2">
                Message received
              </h2>
              <p className="text-sm text-[var(--text-secondary)] max-w-sm">
                We've got your message and will get back to you soon.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input
                  id="subject"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="What's this about?"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="message">Message</Label>
                <Textarea
                  id="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Tell us what you're running into..."
                  rows={6}
                  required
                />
              </div>

              {error && (
                <p className="text-sm text-[var(--destructive)] font-medium">
                  {error}
                </p>
              )}

              <Button type="submit" className="gap-2" disabled={loading}>
                {loading ? (
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
                {loading ? 'Sending...' : 'Send message'}
              </Button>
            </form>
          )}
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6">
            <p className="text-label text-[var(--text-muted)] mb-3">Prefer something else?</p>
            <div className="flex flex-col gap-2">
              <a
                href={`mailto:${SUPPORT_EMAIL}`}
                className="flex items-center gap-3 rounded-lg border border-[var(--border-subtle)] px-4 py-3 text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors"
              >
                <Mail className="h-4 w-4 text-brand" />
                {SUPPORT_EMAIL}
              </a>
              <a
                href={SUPPORT_WHATSAPP}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 rounded-lg border border-[var(--border-subtle)] px-4 py-3 text-sm font-medium text-[var(--text-primary)] hover:bg-[var(--bg-subtle)] transition-colors"
              >
                <MessageCircle className="h-4 w-4 text-brand" />
                Chat on WhatsApp
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
