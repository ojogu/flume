const STORAGE_KEY = 'flume_returnTo'

// Only internal paths are allowed as post-login destinations.
// Never return users to /login itself or into admin-land from public flows.
function isValidReturnTo(path: string | null): path is string {
  if (!path || !path.startsWith('/') || path.startsWith('//') || path === '/login') {
    return false
  }
  if (path.startsWith('/admin')) {
    return false
  }
  return true
}

export function saveReturnTo(path: string | null): void {
  if (isValidReturnTo(path)) {
    sessionStorage.setItem(STORAGE_KEY, path)
  }
}

export function consumeReturnTo(fallback = '/web'): string {
  const stored = sessionStorage.getItem(STORAGE_KEY)
  sessionStorage.removeItem(STORAGE_KEY)
  if (isValidReturnTo(stored)) return stored
  return fallback
}
