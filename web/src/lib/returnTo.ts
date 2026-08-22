const STORAGE_KEY = 'flume_returnTo'

// Only internal paths are allowed as post-login destinations.
function isValidReturnTo(path: string | null): path is string {
  return Boolean(path && path.startsWith('/') && !path.startsWith('//'))
}

export function saveReturnTo(path: string | null): void {
  if (isValidReturnTo(path)) {
    sessionStorage.setItem(STORAGE_KEY, path)
  }
}

export function consumeReturnTo(fallback = '/dashboard'): string {
  const stored = sessionStorage.getItem(STORAGE_KEY)
  sessionStorage.removeItem(STORAGE_KEY)
  if (isValidReturnTo(stored)) return stored
  return fallback
}
