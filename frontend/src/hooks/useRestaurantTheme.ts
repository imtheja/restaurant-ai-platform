import { useQuery } from 'react-query';
import { restaurantApi } from '@services/api';

export interface RestaurantTheme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
  gradients: {
    header: string;
    button: string;
    fab: string;
  };
}

export const useRestaurantTheme = (restaurantSlug: string) => {
  const { data: restaurant } = useQuery(
    ['restaurant', restaurantSlug],
    () => restaurantApi.getBySlug(restaurantSlug),
    {
      staleTime: 2 * 60 * 1000, // Cache for 2 minutes
      cacheTime: 5 * 60 * 1000, // Keep in cache for 5 minutes
    }
  );

  const theme: RestaurantTheme = (restaurant as any)?.theme_config || {
    primary: '#aa8a40',
    secondary: '#d4a854',
    accent: '#ede7d4',
    background: '#ffffff',
    text: '#333333',
    gradients: {
      header: 'linear-gradient(135deg, #aa8a40 0%, #d4a854 50%, #aa8a40 100%)',
      button: 'linear-gradient(135deg, #aa8a40 0%, #d4a854 100%)',
      fab: 'linear-gradient(135deg, #aa8a40 0%, #d4a854 100%)'
    }
  };

  return theme;
};