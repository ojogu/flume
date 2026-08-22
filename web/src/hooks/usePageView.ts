import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { trackPageView } from '@/lib/pageview'

const EXCLUDED_PATHS = ['/callback']

export function usePageView(): void {
  const location = useLocation()

  useEffect(() => {
    if (!EXCLUDED_PATHS.includes(location.pathname)) {
      trackPageView(location.pathname)
    }
  }, [location.pathname])
}
