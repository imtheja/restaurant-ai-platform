import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  mode: 'light' | 'dark';
  primaryColor: string;
  toggleMode: () => void;
  setPrimaryColor: (color: string) => void;
  setRestaurantTheme: (restaurant: any) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      mode: 'light',
      primaryColor: '#1976d2',
      
      toggleMode: () =>
        set((state) => ({
          mode: state.mode === 'light' ? 'dark' : 'light',
        })),
      
      setPrimaryColor: (color: string) =>
        set({ primaryColor: color }),
      
      setRestaurantTheme: (restaurant: any) =>
        set((state) => {
          // Extract theme colors from restaurant branding if available
          const brandColor = restaurant?.settings?.brand_color || state.primaryColor;
          return {
            primaryColor: brandColor,
          };
        }),
    }),
    {
      name: 'restaurant-ai-theme',
    }
  )
);