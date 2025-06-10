-- Restaurant AI Platform Database Initialization
-- This script sets up the database with proper indexes and constraints

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better query performance
-- These will be created automatically when the tables are created via SQLAlchemy
-- but we can add additional custom indexes here if needed

-- Index for restaurant slug lookups
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_restaurants_slug ON restaurants(slug);

-- Index for menu items by restaurant and availability
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_menu_items_restaurant_available 
--     ON menu_items(restaurant_id, is_available) WHERE is_available = true;

-- Index for conversation lookups by restaurant and session
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_restaurant_session 
--     ON conversations(restaurant_id, session_id);

-- Index for messages by conversation and timestamp
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_created 
--     ON messages(conversation_id, created_at);

-- Index for analytics queries
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_restaurant_event_time 
--     ON interaction_analytics(restaurant_id, event_type, timestamp);

-- Insert sample data for development
-- Sample restaurants
INSERT INTO restaurants (id, name, slug, cuisine_type, description, avatar_config, is_active) VALUES 
(
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Mario''s Italian Kitchen',
    'marios-italian',
    'Italian',
    'Authentic Italian cuisine with family recipes passed down through generations',
    '{
        "name": "Sofia",
        "personality": "friendly_knowledgeable",
        "greeting": "Ciao! I''m Sofia, your personal dining assistant at Mario''s. How can I help you discover our delicious Italian specialties today?",
        "tone": "warm",
        "specialInstructions": "Always mention our daily specials, emphasize fresh ingredients and family recipes"
    }',
    true
),
(
    'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
    'Dragon Garden Chinese Bistro',
    'dragon-garden',
    'Chinese',
    'Traditional Chinese cuisine with modern presentation',
    '{
        "name": "Lin",
        "personality": "professional_expert",
        "greeting": "Welcome to Dragon Garden! I''m Lin, your culinary guide. Let me help you explore our authentic Chinese dishes.",
        "tone": "professional",
        "specialInstructions": "Explain cooking methods and ingredient origins, mention spice levels clearly"
    }',
    true
) ON CONFLICT (id) DO NOTHING;

-- Sample categories for Mario's Italian Kitchen
INSERT INTO menu_categories (id, restaurant_id, name, description, display_order) VALUES 
(
    'c1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Appetizers',
    'Start your meal with our traditional Italian appetizers',
    1
),
(
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Pasta',
    'Handmade pasta dishes with authentic Italian sauces',
    2
),
(
    'c3eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Pizza',
    'Wood-fired pizzas with fresh toppings',
    3
),
(
    'c4eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Desserts',
    'Traditional Italian desserts to end your meal perfectly',
    4
) ON CONFLICT (id) DO NOTHING;

-- Sample ingredients
INSERT INTO ingredients (id, name, category, allergen_info) VALUES 
('i1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Spaghetti', 'Pasta', '["gluten"]'),
('i2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Eggs', 'Protein', '["eggs"]'),
('i3eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Pancetta', 'Meat', '[]'),
('i4eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Parmesan Cheese', 'Dairy', '["dairy"]'),
('i5eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'San Marzano Tomatoes', 'Vegetable', '[]'),
('i6eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Fresh Mozzarella', 'Dairy', '["dairy"]'),
('i7eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Fresh Basil', 'Herb', '[]'),
('i8eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Extra Virgin Olive Oil', 'Oil', '[]')
ON CONFLICT (id) DO NOTHING;

-- Sample menu items for Mario's Italian Kitchen
INSERT INTO menu_items (id, restaurant_id, category_id, name, description, price, is_available, is_signature, spice_level, preparation_time, allergen_info, tags) VALUES 
(
    'm1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Spaghetti Carbonara',
    'Creamy pasta with pancetta, parmesan, and fresh eggs - a Roman classic',
    18.99,
    true,
    false,
    0,
    15,
    '["gluten", "eggs", "dairy"]',
    '["traditional", "popular"]'
),
(
    'm2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'c3eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Margherita Pizza',
    'Classic pizza with San Marzano tomatoes, fresh mozzarella, and basil',
    16.99,
    true,
    false,
    0,
    12,
    '["gluten", "dairy"]',
    '["vegetarian", "classic"]'
),
(
    'm3eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Signature Pasta Trio',
    'A combination of our three most popular pasta dishes in smaller portions',
    24.99,
    true,
    true,
    1,
    20,
    '["gluten", "eggs", "dairy", "nuts"]',
    '["signature", "variety", "popular"]'
)
ON CONFLICT (id) DO NOTHING;

-- Sample menu item ingredients relationships
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_primary) VALUES 
('m1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '4', 'oz', true),
('m1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2', 'pieces', true),
('m1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i3eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '2', 'oz', true),
('m1eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i4eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '1', 'cup', true),
('m2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i5eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '1/2', 'cup', true),
('m2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i6eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '4', 'oz', true),
('m2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i7eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '6', 'leaves', false),
('m2eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'i8eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '1', 'tbsp', false)
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;