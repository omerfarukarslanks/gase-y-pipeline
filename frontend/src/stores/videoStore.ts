import { create } from 'zustand'

interface VideoCreationState {
  prompt: string
  languages: string[]
  aspectRatio: string
  aiProvider: string
  ttsProvider: string
  selectedPlatforms: string[]
  bgMusic: string | null
  setPrompt: (prompt: string) => void
  setLanguages: (languages: string[]) => void
  setAspectRatio: (ratio: string) => void
  setAiProvider: (provider: string) => void
  setTtsProvider: (provider: string) => void
  setSelectedPlatforms: (platforms: string[]) => void
  setBgMusic: (trackId: string | null) => void
  reset: () => void
}

const initialState = {
  prompt: '',
  languages: ['en'],
  aspectRatio: '16:9',
  aiProvider: 'openai',
  ttsProvider: 'elevenlabs',
  selectedPlatforms: ['youtube'],
  bgMusic: null as string | null,
}

export const useVideoStore = create<VideoCreationState>()((set) => ({
  ...initialState,
  setPrompt: (prompt) => set({ prompt }),
  setLanguages: (languages) => set({ languages }),
  setAspectRatio: (ratio) => set({ aspectRatio: ratio }),
  setAiProvider: (provider) => set({ aiProvider: provider }),
  setTtsProvider: (provider) => set({ ttsProvider: provider }),
  setSelectedPlatforms: (platforms) => set({ selectedPlatforms: platforms }),
  setBgMusic: (trackId) => set({ bgMusic: trackId }),
  reset: () => set(initialState),
}))
