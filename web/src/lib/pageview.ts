import { API_BASE } from '@/lib/config'

const V1_BASE = API_BASE.replace('/internal', '/v1')

export function trackPageView(path: string): void {
  const referrer = document.referrer || null
  fetch(`${V1_BASE}/analytics/pageview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, referrer }),
  }).catch(() => {})
}
