import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { getOrCreateSession, clearSession, type SessionData } from '@/lib/session'
import type { JobDetailResponse } from '@/lib/web'

export type SourceType = 'url' | 'upload'
export type AppMode = 'preset' | 'advanced'

export interface PipelineStep {
  id: string
  operation: string
  params: Record<string, unknown>
}

interface WebState {
  session: SessionData | null
  sourceType: SourceType
  sourceUri: string
  uploadedFile: { name: string; size: number; type: string } | null
  mode: AppMode
  selectedPreset: string | null
  presetParams: Record<string, unknown>
  pipelineSteps: PipelineStep[]
  currentJobId: string | null
  jobDetail: JobDetailResponse | null
  isSubmitting: boolean
  error: string | null

  initSession: () => Promise<void>
  setSourceType: (t: SourceType) => void
  setSourceUri: (uri: string) => void
  setUploadedFile: (f: { name: string; size: number; type: string } | null) => void
  setMode: (m: AppMode) => void
  selectPreset: (name: string | null) => void
  setPresetParams: (params: Record<string, unknown>) => void
  setPresetParam: (key: string, value: unknown) => void
  setPipelineSteps: (steps: PipelineStep[]) => void
  addPipelineStep: (step: PipelineStep) => void
  removePipelineStep: (id: string) => void
  setJobId: (id: string | null) => void
  setJobDetail: (d: JobDetailResponse | null) => void
  setSubmitting: (v: boolean) => void
  setError: (e: string | null) => void
  decrementJobsRemaining: () => void
  resetUI: () => void
  reset: () => void
  resetJob: () => void
}

const initialState = {
  session: null,
  sourceType: 'url' as SourceType,
  sourceUri: '',
  uploadedFile: null,
  mode: 'preset' as AppMode,
  selectedPreset: null,
  presetParams: {} as Record<string, unknown>,
  pipelineSteps: [],
  currentJobId: null,
  jobDetail: null,
  isSubmitting: false,
  error: null,
}

export const useWebStore = create<WebState>()(
  persist(
    (set) => ({
      ...initialState,

      initSession: async () => {
        const session = await getOrCreateSession()
        set({ session })
      },

      setSourceType: (sourceType) => set({ sourceType }),
      setSourceUri: (sourceUri) => set({ sourceUri }),
      setUploadedFile: (uploadedFile) => set({ uploadedFile }),
      setMode: (mode) => set({ mode }),
      selectPreset: (selectedPreset) => set({ selectedPreset, presetParams: {} }),
      setPresetParams: (presetParams) => set({ presetParams }),
      setPresetParam: (key, value) =>
        set((s) => ({ presetParams: { ...s.presetParams, [key]: value } })),

      setPipelineSteps: (pipelineSteps) => set({ pipelineSteps }),

      addPipelineStep: (step) =>
        set((s) => ({ pipelineSteps: [...s.pipelineSteps, step] })),

      removePipelineStep: (id) =>
        set((s) => ({ pipelineSteps: s.pipelineSteps.filter((p) => p.id !== id) })),

      setJobId: (currentJobId) => set({ currentJobId }),
      setJobDetail: (jobDetail) => set({ jobDetail }),
      setSubmitting: (isSubmitting) => set({ isSubmitting }),
      setError: (error) => set({ error }),

      resetJob: () => set({ currentJobId: null, jobDetail: null, error: null }),

      decrementJobsRemaining: () =>
        set((s) => ({
          session: s.session
            ? { ...s.session, jobsRemaining: Math.max(0, s.session.jobsRemaining - 1) }
            : null,
        })),

      resetUI: () =>
        set({
          sourceUri: '',
          uploadedFile: null,
          mode: 'preset',
          selectedPreset: null,
          presetParams: {},
          pipelineSteps: [],
          currentJobId: null,
          jobDetail: null,
          isSubmitting: false,
          error: null,
        }),

      reset: () => {
        clearSession()
        set({ ...initialState })
      },
    }),
    {
      name: 'flume-web-store',
      partialize: (state) => ({
        session: state.session,
        sourceType: state.sourceType,
        sourceUri: state.sourceUri,
        mode: state.mode,
        selectedPreset: state.selectedPreset,
      }),
    },
  ),
)
