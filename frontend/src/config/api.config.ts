// API Configuration for different environments
export const API_CONFIG = {
  development: {
    RESTAURANT_SERVICE: 'http://localhost:8001',
    MENU_SERVICE: 'http://localhost:8002',
    AI_SERVICE: 'http://localhost:8003',
  },
  production: {
    RESTAURANT_SERVICE: import.meta.env.VITE_RESTAURANT_SERVICE_URL || '',
    MENU_SERVICE: import.meta.env.VITE_MENU_SERVICE_URL || '',
    AI_SERVICE: import.meta.env.VITE_AI_SERVICE_URL || '',
  }
};

export const getApiConfig = () => {
  const env = import.meta.env.MODE;
  return API_CONFIG[env as keyof typeof API_CONFIG] || API_CONFIG.development;
};

export const getServiceUrl = (service: 'RESTAURANT' | 'MENU' | 'AI') => {
  const config = getApiConfig();
  switch(service) {
    case 'RESTAURANT':
      return config.RESTAURANT_SERVICE;
    case 'MENU':
      return config.MENU_SERVICE;
    case 'AI':
      return config.AI_SERVICE;
    default:
      return config.RESTAURANT_SERVICE;
  }
};