-- Migration: Add AI Configuration Support
-- Description: Add AI configuration fields to restaurants table and create supporting tables
-- Version: 001
-- Date: 2025-07-06

-- Add AI configuration columns to restaurants table
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS ai_config JSON DEFAULT '{
  "mode": "text_only",
  "provider": "openai",
  "features": {
    "speech_synthesis": false,
    "speech_recognition": false,
    "streaming": true,
    "voice_selection": false
  },
  "model_config": {
    "model_name": "gpt-4o-mini",
    "max_tokens": 150,
    "temperature": 0.7,
    "context_messages": 10
  },
  "performance": {
    "streaming_enabled": true,
    "cache_responses": true,
    "max_daily_requests": 1000,
    "max_daily_cost_usd": 10.0,
    "rate_limit_per_minute": 60
  }
}'::json;

-- Add AI provider information
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50) DEFAULT 'openai';

-- Add AI model configuration
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS ai_model VARCHAR(100) DEFAULT 'gpt-4o-mini';

-- Add features enabled tracking
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS features_enabled JSON DEFAULT '{}'::json;

-- Create AI providers table for future extensibility
CREATE TABLE IF NOT EXISTS ai_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    api_endpoint VARCHAR(500),
    available_models JSON DEFAULT '[]'::json,
    rate_limits JSON DEFAULT '{}'::json,
    cost_per_token JSON DEFAULT '{}'::json,
    is_active BOOLEAN DEFAULT TRUE,
    capabilities JSON DEFAULT '{
        "text_generation": true,
        "speech_synthesis": false,
        "speech_recognition": false,
        "streaming": false,
        "function_calling": false
    }'::json,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default OpenAI provider
INSERT INTO ai_providers (name, display_name, api_endpoint, available_models, capabilities, cost_per_token)
VALUES (
    'openai',
    'OpenAI GPT',
    'https://api.openai.com/v1',
    '[
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "context_window": 128000},
        {"id": "gpt-4o", "name": "GPT-4o", "context_window": 128000},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context_window": 128000},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_window": 16385}
    ]'::json,
    '{
        "text_generation": true,
        "speech_synthesis": true,
        "speech_recognition": true,
        "streaming": true,
        "function_calling": true
    }'::json,
    '{
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }'::json
) ON CONFLICT (name) DO NOTHING;

-- Create AI usage analytics table
CREATE TABLE IF NOT EXISTS ai_usage_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL DEFAULT 'openai',
    model VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    cost_usd DECIMAL(10,4) DEFAULT 0.0000,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_type VARCHAR(100),
    endpoint VARCHAR(100),
    user_agent VARCHAR(500),
    ip_address INET,
    session_id VARCHAR(255),
    date DATE DEFAULT CURRENT_DATE,
    hour INTEGER DEFAULT EXTRACT(HOUR FROM NOW()),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create AI configuration history table for audit trail
CREATE TABLE IF NOT EXISTS ai_config_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID REFERENCES restaurants(id) ON DELETE CASCADE,
    config_before JSON,
    config_after JSON NOT NULL,
    changed_by VARCHAR(255),
    change_reason TEXT,
    change_type VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_restaurants_ai_provider ON restaurants(ai_provider);
CREATE INDEX IF NOT EXISTS idx_restaurants_ai_model ON restaurants(ai_model);
CREATE INDEX IF NOT EXISTS idx_ai_usage_restaurant_date ON ai_usage_analytics(restaurant_id, date);
CREATE INDEX IF NOT EXISTS idx_ai_usage_provider_model ON ai_usage_analytics(provider, model);
CREATE INDEX IF NOT EXISTS idx_ai_usage_success ON ai_usage_analytics(success, created_at);
CREATE INDEX IF NOT EXISTS idx_ai_config_history_restaurant ON ai_config_history(restaurant_id, created_at);

-- Add updated_at trigger for restaurants table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'update_restaurants_updated_at'
    ) THEN
        CREATE TRIGGER update_restaurants_updated_at 
            BEFORE UPDATE ON restaurants 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- Update existing restaurants with default AI configuration
UPDATE restaurants 
SET ai_config = '{
    "mode": "text_only",
    "provider": "openai",
    "features": {
        "speech_synthesis": false,
        "speech_recognition": false,
        "streaming": true,
        "voice_selection": false
    },
    "model_config": {
        "model_name": "gpt-4o-mini",
        "max_tokens": 150,
        "temperature": 0.7,
        "context_messages": 10
    },
    "performance": {
        "streaming_enabled": true,
        "cache_responses": true,
        "max_daily_requests": 1000,
        "max_daily_cost_usd": 10.0,
        "rate_limit_per_minute": 60
    }
}'::json
WHERE ai_config IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN restaurants.ai_config IS 'JSON configuration for AI features and settings';
COMMENT ON COLUMN restaurants.ai_provider IS 'AI provider name (openai, anthropic, etc.)';
COMMENT ON COLUMN restaurants.ai_model IS 'Specific AI model being used';
COMMENT ON COLUMN restaurants.features_enabled IS 'Enabled features for this restaurant';

COMMENT ON TABLE ai_providers IS 'Available AI providers and their capabilities';
COMMENT ON TABLE ai_usage_analytics IS 'Analytics and usage tracking for AI features';
COMMENT ON TABLE ai_config_history IS 'Audit trail for AI configuration changes';

-- Migration completed successfully
SELECT 'Migration 001_add_ai_configuration.sql completed successfully' AS status;