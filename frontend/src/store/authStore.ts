/**
 * authStore.ts - Global authentication state management
 * 
 * Author: Md. Tanvir Hossain
 * 
 * Using Zustand instead of Redux because it's way simpler for a project
 * this size. The persist middleware saves to localStorage so users stay
 * logged in across refreshes. For production, might want to add token
 * refresh logic here.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (token, user) =>
        set({ token, user, isAuthenticated: true }),
      logout: () =>
        set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
)
