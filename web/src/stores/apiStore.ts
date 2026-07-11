import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ApiState {
  activeApiKey: string | null // This should be the full flm_... key
  activeKeyName: string | null
  setActiveApiKey: (key: string | null, name: string | null) => void
}

export const useApiStore = create<ApiState>()(
  persist(
    (set) => ({
      activeApiKey: null,
      activeKeyName: null,
      setActiveApiKey: (activeApiKey, activeKeyName) => set({ activeApiKey, activeKeyName }),
    }),
    {
      name: 'flume-api-store',
    }
  )
)
