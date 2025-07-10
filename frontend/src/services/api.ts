import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { APIResponse, PaginatedResponse } from '../types';

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: (import.meta.env as any).VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// In development, all services go through nginx gateway to avoid CORS
// In production, we can use direct service URLs
const isDevelopment = (import.meta.env as any).DEV || (import.meta.env as any).VITE_APP_ENV !== 'production';

// On Render, all API calls go through restaurant service (no gateway)
// In development, all calls go through nginx gateway
const aiApi: AxiosInstance = axios.create({
  baseURL: (import.meta.env as any).VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Speech API also uses same base URL (goes through restaurant service on Render)
const speechApi: AxiosInstance = axios.create({
  baseURL: (import.meta.env as any).VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for main API
api.interceptors.request.use(
  (config) => {
    // Add request timestamp for debugging
    (config as any).metadata = { startTime: new Date() };
    
    // Add auth token if available (for future use)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Request interceptor for AI API
aiApi.interceptors.request.use(
  (config) => {
    // Add request timestamp for debugging
    (config as any).metadata = { startTime: new Date() };
    
    // Add auth token if available (for future use)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for main API
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time for debugging
    const endTime = new Date();
    const duration = endTime.getTime() - (response.config as any).metadata?.startTime?.getTime();
    
    if ((import.meta.env as any).DEV) {
      console.log(`${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
    
    return response;
  },
  (error: AxiosError) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - clear auth token
      localStorage.removeItem('auth_token');
      // Redirect to login if needed
    }
    
    if (error.response?.status === 429) {
      // Rate limited
      console.warn('Rate limit exceeded');
    }
    
    return Promise.reject(error);
  }
);

// Response interceptor for AI API
aiApi.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time for debugging
    const endTime = new Date();
    const duration = endTime.getTime() - (response.config as any).metadata?.startTime?.getTime();
    
    if ((import.meta.env as any).DEV) {
      console.log(`AI ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
    
    return response;
  },
  (error: AxiosError) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - clear auth token
      localStorage.removeItem('auth_token');
      // Redirect to login if needed
    }
    
    if (error.response?.status === 429) {
      // Rate limited
      console.warn('Rate limit exceeded');
    }
    
    return Promise.reject(error);
  }
);

// Request interceptor for Speech API
speechApi.interceptors.request.use(
  (config) => {
    // Add request timestamp for debugging
    (config as any).metadata = { startTime: new Date() };
    
    // Add auth token if available (for future use)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for Speech API
speechApi.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response time for debugging
    const endTime = new Date();
    const duration = endTime.getTime() - (response.config as any).metadata?.startTime?.getTime();
    
    if ((import.meta.env as any).DEV) {
      console.log(`Speech ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
    
    return response;
  },
  (error: AxiosError) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - clear auth token
      localStorage.removeItem('auth_token');
      // Redirect to login if needed
    }
    
    if (error.response?.status === 429) {
      // Rate limited
      console.warn('Speech API rate limit exceeded');
    }
    
    return Promise.reject(error);
  }
);

// Generic API response handler
const handleApiResponse = <T>(response: AxiosResponse<APIResponse<T>>): T => {
  if (response.data.success) {
    return response.data.data as T;
  } else {
    throw new Error(response.data.message || 'API request failed');
  }
};

// Generic API error handler
const handleApiError = (error: AxiosError): never => {
  if (error.response?.data) {
    const apiError = error.response.data as APIResponse;
    const message = apiError.message || 'An error occurred';
    const errors = apiError.errors || [];
    
    const errorMessage = errors.length > 0 ? `${message}: ${errors.join(', ')}` : message;
    throw new Error(errorMessage);
  } else if (error.request) {
    throw new Error('Network error - please check your connection');
  } else {
    throw new Error(error.message || 'An unexpected error occurred');
  }
};

// Restaurant API
export const restaurantApi = {
  // Get restaurant by slug
  getBySlug: async (slug: string) => {
    try {
      const response = await api.get(`/api/v1/restaurants/${slug}`);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Get restaurant menu
  getMenu: async (slug: string, params?: { category_id?: string; include_unavailable?: boolean }) => {
    try {
      const response = await api.get(`/api/v1/restaurants/${slug}/menu`, { params });
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Get restaurant categories
  getCategories: async (slug: string) => {
    try {
      const response = await api.get(`/api/v1/restaurants/${slug}/categories`);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Get avatar configuration
  getAvatarConfig: async (slug: string) => {
    try {
      const response = await api.get(`/api/v1/restaurants/${slug}/avatar`);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Get menu item details
  getMenuItem: async (slug: string, itemId: string) => {
    try {
      const response = await api.get(`/api/v1/restaurants/${slug}/items/${itemId}`);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Search restaurants
  search: async (params: { q: string; cuisine_type?: string; limit?: number }) => {
    try {
      const response = await api.get('/api/v1/search/restaurants', { params });
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },
};

// Chat API (uses AI service)
export const chatApi = {
  // Send chat message
  sendMessage: async (restaurantSlug: string, data: {
    message: string;
    session_id: string;
    context?: Record<string, any>;
  }) => {
    try {
      const response = await aiApi.post(`/api/v1/restaurants/${restaurantSlug}/chat`, data);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Stream message to AI for real-time responses
  sendMessageStream: async (restaurantSlug: string, data: {
    message: string;
    session_id: string;
    context?: Record<string, any>;
  }, onChunk: (chunk: string) => void, onComplete: () => void, onError: (error: string) => void) => {
    try {
      const response = await fetch(`${(import.meta.env as any).VITE_API_BASE_URL}/api/v1/restaurants/${restaurantSlug}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body reader available');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'token') {
                onChunk(data.content);
              } else if (data.type === 'done') {
                onComplete();
                return data.message_id;
              } else if (data.type === 'error') {
                onError(data.error);
                return;
              }
            } catch (e) {
              console.warn('Failed to parse streaming data:', line);
            }
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Unknown streaming error');
    }
  },

  // Get conversation suggestions
  getSuggestions: async (restaurantSlug: string, context?: string) => {
    try {
      const response = await aiApi.get(`/api/v1/restaurants/${restaurantSlug}/chat/suggestions`, {
        params: { context }
      });
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Submit feedback
  submitFeedback: async (restaurantSlug: string, feedbackData: Record<string, any>) => {
    try {
      const response = await aiApi.post(`/api/v1/restaurants/${restaurantSlug}/chat/feedback`, feedbackData);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Get chat analytics
  getAnalytics: async (restaurantSlug: string, days: number = 7) => {
    try {
      const response = await aiApi.get(`/api/v1/restaurants/${restaurantSlug}/chat/analytics`, {
        params: { days }
      });
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // Speech API methods
  transcribeAudio: async (formData: FormData): Promise<{ transcript: string }> => {
    try {
      const response = await speechApi.post('/api/v1/speech/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  synthesizeSpeech: async (data: {
    text: string;
    voice?: string;
    restaurant_slug?: string;
  }): Promise<AxiosResponse<Blob>> => {
    try {
      const formData = new FormData();
      formData.append('text', data.text);
      formData.append('voice', data.voice || 'nova');
      if (data.restaurant_slug) {
        formData.append('restaurant_slug', data.restaurant_slug);
      }

      const response = await speechApi.post('/api/v1/speech/synthesize', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', // Important for audio data
      });
      return response; // Return full response for blob data
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  getAvailableVoices: async () => {
    try {
      const response = await speechApi.get('/api/v1/speech/voices');
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  getSpeechConfig: async () => {
    try {
      const response = await speechApi.get('/api/v1/speech/config');
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  // New dynamic AI configuration methods
  getAIConfig: async (restaurantSlug: string) => {
    try {
      const response = await aiApi.get(`/api/v1/restaurants/${restaurantSlug}/ai/config`);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  updateAIConfig: async (restaurantSlug: string, config: any) => {
    try {
      const response = await aiApi.put(`/api/v1/restaurants/${restaurantSlug}/ai/config`, config);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  getAIVoices: async (restaurantSlug: string) => {
    try {
      const response = await aiApi.get(`/api/v1/restaurants/${restaurantSlug}/ai/voices`);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },

  getAIHealth: async (restaurantSlug: string) => {
    try {
      const response = await aiApi.get(`/api/v1/restaurants/${restaurantSlug}/ai/health`);
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },
};

// Menu Image API
export const menuImageApi = {
  // Upload image for menu item
  uploadImage: async (restaurantId: string, itemId: string, file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post(
        `/api/v1/restaurants/${restaurantId}/menu/items/${itemId}/image`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return handleApiResponse(response);
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },
};

// Admin API (for future use)
export const adminApi = {
  // Restaurant management
  restaurants: {
    list: async (params?: { page?: number; per_page?: number; active_only?: boolean }) => {
      try {
        const response = await api.get('/api/v1/admin/restaurants', { params });
        return response.data as PaginatedResponse<any>;
      } catch (error) {
        handleApiError(error as AxiosError);
      }
    },

    create: async (data: Record<string, any>) => {
      try {
        const response = await api.post('/api/v1/admin/restaurants', data);
        return handleApiResponse(response);
      } catch (error) {
        handleApiError(error as AxiosError);
      }
    },

    update: async (id: string, data: Record<string, any>) => {
      try {
        const response = await api.put(`/api/v1/admin/restaurants/${id}`, data);
        return handleApiResponse(response);
      } catch (error) {
        handleApiError(error as AxiosError);
      }
    },

    delete: async (id: string) => {
      try {
        const response = await api.delete(`/api/v1/admin/restaurants/${id}`);
        return handleApiResponse(response);
      } catch (error) {
        handleApiError(error as AxiosError);
      }
    },
  },

  // Avatar configuration
  avatar: {
    update: async (restaurantId: string, config: Record<string, any>) => {
      try {
        const response = await api.put(`/api/v1/admin/restaurants/${restaurantId}/avatar`, config);
        return handleApiResponse(response);
      } catch (error) {
        handleApiError(error as AxiosError);
      }
    },
  },
};

// Health check
export const healthApi = {
  check: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      handleApiError(error as AxiosError);
    }
  },
};

export default api;