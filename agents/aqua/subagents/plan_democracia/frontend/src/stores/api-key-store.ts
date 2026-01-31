import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ApiKeyState {
  apiKey: string | null
  setApiKey: (key: string) => void
  clearApiKey: () => void
  hasApiKey: () => boolean
  getApiKey: () => string | null
}

export const useApiKeyStore = create<ApiKeyState>()(
  persist(
    (set, get) => ({
      apiKey: null,
      setApiKey: (key: string) => set({ apiKey: key }),
      clearApiKey: () => set({ apiKey: null }),
      hasApiKey: () => get().apiKey !== null && get().apiKey !== '',
      getApiKey: () => get().apiKey,
    }),
    {
      name: 'api-key-storage',
    }
  )
)

// Helper para usar fuera de componentes React (en funciones de API/fetch)
export const getApiKey = () => useApiKeyStore.getState().apiKey
