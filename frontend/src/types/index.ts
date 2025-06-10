// API Response Types
export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  errors?: string[];
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  meta: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

// Restaurant Types
export interface Restaurant {
  id: string;
  name: string;
  slug: string;
  cuisine_type?: string;
  description?: string;
  avatar_config?: AvatarConfig;
  contact_info?: Record<string, any>;
  settings?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AvatarConfig {
  name: string;
  personality: 'friendly_knowledgeable' | 'professional_formal' | 'casual_fun' | 'expert_chef';
  greeting: string;
  tone: 'warm' | 'professional' | 'enthusiastic' | 'casual';
  special_instructions?: string;
}

// Menu Types
export interface MenuCategory {
  id: string;
  restaurant_id: string;
  name: string;
  description?: string;
  display_order: number;
  is_active: boolean;
  items?: MenuItem[];
  created_at: string;
  updated_at: string;
}

export interface MenuItem {
  id: string;
  restaurant_id: string;
  category_id?: string;
  name: string;
  description?: string;
  price: number;
  image_url?: string;
  is_available: boolean;
  is_signature: boolean;
  spice_level: number;
  preparation_time?: number;
  allergen_info?: string[];
  tags?: string[];
  display_order: number;
  category?: MenuCategory;
  ingredients?: MenuItemIngredient[];
  created_at: string;
  updated_at: string;
}

export interface Ingredient {
  id: string;
  name: string;
  category?: string;
  allergen_info?: string[];
  nutritional_info?: Record<string, any>;
  is_active: boolean;
  created_at: string;
}

export interface MenuItemIngredient {
  ingredient_id: string;
  quantity?: string;
  unit?: string;
  is_optional: boolean;
  is_primary: boolean;
  ingredient: Ingredient;
}

// Chat Types
export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender_type: 'customer' | 'ai';
  content: string;
  message_type: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Conversation {
  id: string;
  restaurant_id: string;
  session_id: string;
  customer_id?: string;
  context?: Record<string, any>;
  metadata?: Record<string, any>;
  is_active: boolean;
  started_at: string;
  last_activity: string;
  messages: ChatMessage[];
}

export interface ChatRequest {
  message: string;
  session_id: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  suggestions?: string[];
  recommendations?: MenuRecommendation[];
  conversation_id: string;
  message_id: string;
}

export interface MenuRecommendation {
  item_name: string;
  reason: string;
  item_id?: string;
}

// UI State Types
export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

export interface MenuState extends LoadingState {
  restaurant?: Restaurant;
  categories: MenuCategory[];
  items: MenuItem[];
  selectedCategory?: string;
  searchQuery: string;
  showUnavailable: boolean;
}

export interface ChatState extends LoadingState {
  conversation?: Conversation;
  messages: ChatMessage[];
  sessionId: string;
  isTyping: boolean;
  suggestions: string[];
}

// Form Types
export interface MenuItemForm {
  name: string;
  description: string;
  price: number;
  category_id?: string;
  image_url?: string;
  is_signature: boolean;
  spice_level: number;
  preparation_time?: number;
  tags: string[];
  ingredients: MenuItemIngredientForm[];
}

export interface MenuItemIngredientForm {
  ingredient_id: string;
  quantity?: string;
  unit?: string;
  is_optional: boolean;
  is_primary: boolean;
}

export interface RestaurantForm {
  name: string;
  slug: string;
  cuisine_type: string;
  description: string;
  contact_info: {
    phone?: string;
    email?: string;
    address?: string;
  };
}

export interface AvatarConfigForm {
  name: string;
  personality: AvatarConfig['personality'];
  greeting: string;
  tone: AvatarConfig['tone'];
  special_instructions: string;
}

// Filter and Search Types
export interface MenuFilters {
  category?: string;
  search?: string;
  allergens?: string[];
  dietary_tags?: string[];
  price_range?: [number, number];
  spice_level?: number[];
  available_only?: boolean;
}

export interface SearchResult {
  restaurants: Restaurant[];
  total: number;
}

// Analytics Types
export interface AnalyticsData {
  total_conversations: number;
  total_messages: number;
  popular_items: Array<{
    item_name: string;
    mentions: number;
  }>;
  common_questions: Array<{
    question: string;
    frequency: number;
  }>;
  avg_session_duration: number;
  customer_satisfaction: number;
  period_days: number;
  last_updated: string;
}

// Error Types
export interface ApiError {
  message: string;
  errors?: string[];
  status?: number;
}

// Theme Types
export interface ThemeConfig {
  mode: 'light' | 'dark';
  primaryColor: string;
  restaurant?: Restaurant;
}

// Utility Types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequireAtLeastOne<T, Keys extends keyof T = keyof T> = 
  Pick<T, Exclude<keyof T, Keys>> & 
  { [K in Keys]-?: Required<Pick<T, K>> & Partial<Pick<T, Exclude<Keys, K>>> }[Keys];

// Event Types
export interface ChatEvent {
  type: 'message' | 'typing' | 'suggestion_click' | 'recommendation_click';
  data: any;
}

export interface MenuEvent {
  type: 'item_view' | 'category_change' | 'search' | 'filter_change';
  data: any;
}