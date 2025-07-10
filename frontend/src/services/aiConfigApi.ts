/**
 * AI Configuration API Service
 * Handles dynamic AI configuration for restaurants
 */
import axios from 'axios';

// AI Configuration Types
export interface AIConfig {
  mode: 'text_only' | 'speech_enabled' | 'hybrid';
  speech_synthesis_enabled: boolean;
  speech_recognition_enabled: boolean;
  voice_selection_enabled: boolean;
  default_voice: string;
  streaming_enabled: boolean;
  auto_play: boolean;
  max_tokens: number;
}

export interface UpdateAIConfigRequest {
  mode: 'text_only' | 'speech_enabled' | 'hybrid';
  speech_synthesis: boolean;
  speech_recognition: boolean;
  default_voice: string;
  voice_selection_enabled: boolean;
  max_tokens: number;
  temperature: number;
  streaming_enabled: boolean;
  cache_responses: boolean;
}

export interface Voice {
  id: string;
  name: string;
  description: string;
  gender: string;
  recommended_for: string;
}

export interface VoicesResponse {
  voices: Voice[];
}

// Create AI Config API client
const createAIConfigApi = (baseURL: string) => {
  const client = axios.create({
    baseURL,
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for logging
  client.interceptors.request.use(
    (config) => {
      console.log(`[AI Config API] ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('[AI Config API] Request error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => {
      return response.data;
    },
    (error) => {
      console.error('[AI Config API] Response error:', error);
      
      if (error.response?.status === 404) {
        throw new Error('AI configuration not found');
      } else if (error.response?.status >= 500) {
        throw new Error('AI service temporarily unavailable');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Failed to communicate with AI service');
      }
    }
  );

  return {
    // Get AI configuration for a restaurant
    getAIConfig: async (restaurantSlug: string): Promise<AIConfig> => {
      const response = await client.get(`/api/v1/restaurants/${restaurantSlug}/ai/config`);
      return response.data;
    },

    // Update AI configuration for a restaurant
    updateAIConfig: async (
      restaurantSlug: string,
      config: UpdateAIConfigRequest
    ): Promise<AIConfig> => {
      const response = await client.put(`/api/v1/restaurants/${restaurantSlug}/ai/config`, config);
      return response.data;
    },

    // Get available voices
    getAvailableVoices: async (restaurantSlug: string): Promise<VoicesResponse> => {
      const response = await client.get(`/api/v1/restaurants/${restaurantSlug}/ai/voices`);
      return response.data;
    },

    // Check AI service health
    getAIHealth: async (restaurantSlug: string): Promise<any> => {
      const response = await client.get(`/api/v1/restaurants/${restaurantSlug}/ai/health`);
      return response;
    },

    // Chat with streaming (new dynamic endpoint)
    chatStream: async (
      restaurantSlug: string,
      message: string,
      sessionId: string,
      context: any = {}
    ): Promise<ReadableStream> => {
      const response = await fetch(`${baseURL}/restaurants/${restaurantSlug}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          context,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat stream error: ${response.status}`);
      }

      return response.body!;
    },

    // Legacy speech config endpoint (for backward compatibility)
    getLegacySpeechConfig: async (): Promise<any> => {
      const response = await client.get('/speech/config');
      return response;
    },
  };
};

// Create the API client instance
const AI_SERVICE_URL = (import.meta.env as any).VITE_AI_SERVICE_URL || 'http://localhost:8003/api/v1';
export const aiConfigApi = createAIConfigApi(AI_SERVICE_URL);

// Helper functions
export const mapLegacyToModern = (legacyConfig: any): Partial<AIConfig> => {
  return {
    mode: legacyConfig.text_only_mode ? 'text_only' : 'hybrid',
    speech_synthesis_enabled: !legacyConfig.text_only_mode && legacyConfig.speech_synthesis_enabled,
    speech_recognition_enabled: !legacyConfig.text_only_mode && legacyConfig.speech_recognition_enabled,
    streaming_enabled: true,
    max_tokens: 150,
    default_voice: 'nova',
    voice_selection_enabled: !legacyConfig.text_only_mode,
    auto_play: !legacyConfig.text_only_mode,
  };
};

export const getDefaultConfig = (): AIConfig => {
  return {
    mode: 'text_only',
    speech_synthesis_enabled: false,
    speech_recognition_enabled: false,
    voice_selection_enabled: false,
    default_voice: 'nova',
    streaming_enabled: true,
    auto_play: false,
    max_tokens: 150,
  };
};