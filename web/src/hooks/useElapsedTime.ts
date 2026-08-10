import { useEffect, useState } from 'react'

export function useElapsedTime(
  startTime: string | null,
  endTime: string | null,
  isRunning: boolean,
) {
  const getElapsed = () => {
    if (!startTime) return 0

    const start = new Date(startTime).getTime()
    const end = endTime ? new Date(endTime).getTime() : Date.now()
    return Math.max(0, end - start)
  }

  const [elapsed, setElapsed] = useState(getElapsed)

  useEffect(() => {
    if (!startTime) {
      setElapsed(0)
      return
    }

    setElapsed(getElapsed())

    if (!isRunning) return

    const interval = window.setInterval(() => {
      setElapsed(getElapsed())
    }, 1000)

    return () => window.clearInterval(interval)
  }, [startTime, endTime, isRunning])

  return elapsed
}
