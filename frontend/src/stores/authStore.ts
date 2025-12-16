import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types';
import { authApi } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(email, password);
          localStorage.setItem('token', response.access_token);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isInitialized: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || '로그인에 실패했습니다.',
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register(email, password, name);
          localStorage.setItem('token', response.access_token);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isInitialized: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || '회원가입에 실패했습니다.',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      checkAuth: async () => {
        const token = localStorage.getItem('token');
        if (!token) {
          set({ isAuthenticated: false, user: null, token: null, isInitialized: true });
          return;
        }

        try {
          const user = await authApi.getMe();
          set({ user, token, isAuthenticated: true, isInitialized: true });
        } catch {
          localStorage.removeItem('token');
          set({ isAuthenticated: false, user: null, token: null, isInitialized: true });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
