import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type Theme = 'light' | 'dark'

interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
  initializeTheme: () => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      setTheme: (theme: Theme) => set({ theme }),
      toggleTheme: () => {
        const currentTheme = get().theme
        set({ theme: currentTheme === 'light' ? 'dark' : 'light' })
      },
      initializeTheme: () => {
        // Check if theme is stored in localStorage
        const storedTheme = localStorage.getItem('theme-store')
        if (storedTheme) {
          try {
            const parsed = JSON.parse(storedTheme)
            if (parsed.state?.theme) {
              set({ theme: parsed.state.theme })
            }
          } catch (error) {
            console.error('Error parsing stored theme:', error)
          }
        } else {
          // Check system preference
          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
          set({ theme: prefersDark ? 'dark' : 'light' })
        }
      },
    }),
    {
      name: 'theme-store',
    }
  )
)