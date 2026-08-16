'use client';

import { useState } from 'react';
import { Mail, MessageCircle, Send, LoaderCircle, CheckCircle2 } from 'lucide-react';

const API_URL = 'https://api.flume.ojogulabs.xyz/v1/support/contact';
const SUPPORT_EMAIL = 'support@ojogulabs.xyz';
const SUPPORT_WHATSAPP = 'https://wa.me/2349065011334';

const inputClass =
  'w-full rounded-lg border border-[var(--border)] bg-[var(--bg-subtle)] px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] outline-none transition-colors focus:border-[var(--brand)]';
const labelClass = 'mb-1.5 block text-sm font-medium';

export function ContactForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSent(false);

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, subject, message }),
      });
      const body = await res.json();
      if (res.ok && body.status === 'success') {
        setSent(true);
        setName('');
        setEmail('');
        setSubject('');
        setMessage('');
      } else {
        setError(body.message || 'Something went wrong. Please try again.');
      }
    } catch {
      setError('Failed to connect to the server. Please reach us directly.');
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-subtle)] p-8 text-center">
        <CheckCircle2 className="mx-auto mb-3 h-10 w-10 text-[var(--brand)]" />
        <p className="font-semibold">Message received</p>
        <p className="mt-1 text-sm text-[var(--text-muted)]">
          We've got your message and will get back to you soon.
        </p>
      </div>
    );
  }

  return (
    <div className="my-6 rounded-xl border border-[var(--border)] bg-[var(--bg-subtle)] p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className={labelClass} htmlFor="cf-name">Name</label>
            <input
              id="cf-name"
              className={inputClass}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              required
            />
          </div>
          <div>
            <label className={labelClass} htmlFor="cf-email">Email</label>
            <input
              id="cf-email"
              type="email"
              className={inputClass}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>
        </div>

        <div>
          <label className={labelClass} htmlFor="cf-subject">Subject</label>
          <input
            id="cf-subject"
            className={inputClass}
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="What's this about?"
            required
          />
        </div>

        <div>
          <label className={labelClass} htmlFor="cf-message">Message</label>
          <textarea
            id="cf-message"
            className={`${inputClass} min-h-32 resize-y`}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Tell us what you're running into..."
            rows={6}
            required
          />
        </div>

        {error && (
          <p className="text-sm font-medium text-red-600 dark:text-red-400">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg bg-[var(--brand)] px-4 py-2 text-sm font-medium text-white transition-colors hover:opacity-90 disabled:opacity-60"
        >
          {loading ? (
            <LoaderCircle className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
          {loading ? 'Sending...' : 'Send message'}
        </button>
      </form>

      <div className="mt-6 border-t border-[var(--border)] pt-4">
        <p className="mb-2 text-sm text-[var(--text-muted)]">Prefer something else?</p>
        <div className="flex flex-wrap gap-3">
          <a
            href={`mailto:${SUPPORT_EMAIL}`}
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--brand)] hover:underline underline-offset-4"
          >
            <Mail className="h-4 w-4" />
            {SUPPORT_EMAIL}
          </a>
          <a
            href={SUPPORT_WHATSAPP}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--brand)] hover:underline underline-offset-4"
          >
            <MessageCircle className="h-4 w-4" />
            Chat on WhatsApp
          </a>
        </div>
      </div>
    </div>
  );
}
