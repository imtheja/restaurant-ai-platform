-- Migration: Add Restaurant Theme and Menu Images
-- Description: Add theme configuration to restaurants and image URLs to menu items
-- Version: 002
-- Date: 2025-07-06

-- Add theme configuration to restaurants table
ALTER TABLE restaurants 
ADD COLUMN IF NOT EXISTS theme_config JSON DEFAULT '{
  "primary": "#FF6B9D",
  "secondary": "#FF8E53",
  "accent": "#FFD93D",
  "background": "#FFFFFF",
  "text": "#333333",
  "gradients": {
    "header": "linear-gradient(135deg, #FF6B9D 0%, #FF8E53 50%, #FFD93D 100%)",
    "button": "linear-gradient(135deg, #FF8E53 0%, #FFD93D 100%)",
    "fab": "linear-gradient(135deg, #FF6B9D 0%, #FF8E53 50%, #FFD93D 100%)"
  }
}'::json;

-- Add image_url to menu_items if not exists
ALTER TABLE menu_items 
ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);

-- Update Baker Betty's/Chip Cookies restaurant with proper theme
UPDATE restaurants 
SET 
    name = 'Chip Cookies',
    theme_config = '{
      "primary": "#aa8a40",
      "secondary": "#d4a854",
      "accent": "#ede7d4",
      "background": "#ffffff",
      "text": "#333333",
      "gradients": {
        "header": "linear-gradient(135deg, #aa8a40 0%, #d4a854 50%, #aa8a40 100%)",
        "button": "linear-gradient(135deg, #aa8a40 0%, #d4a854 100%)",
        "fab": "linear-gradient(135deg, #aa8a40 0%, #d4a854 100%)"
      }
    }'::json
WHERE slug = 'baker-bettys';

-- Update menu items with image URLs for Chip Cookies
-- First, let's update based on menu item names
UPDATE menu_items 
SET image_url = CASE 
    WHEN LOWER(name) = 'og chip' THEN '/images/menu-items/og-chip.png'
    WHEN LOWER(name) = 'sw chip' THEN '/images/menu-items/sw-chip.png'
    WHEN LOWER(name) = 'sugar chip' THEN '/images/menu-items/sugar-chip.png'
    WHEN LOWER(name) = 's''mores chip' OR LOWER(name) = 'smores chip' THEN '/images/menu-items/smores-chip.png'
    WHEN LOWER(name) = 'biscoff chip' THEN '/images/menu-items/biscoff-chip.png'
    WHEN LOWER(name) = 'bts chip' THEN '/images/menu-items/bts-chip.png'
    WHEN LOWER(name) = 'tres leches chip' THEN '/images/menu-items/tres-leches-chip.png'
    WHEN LOWER(name) = 'oreo dunk chip' THEN '/images/menu-items/oreo-dunk-chip.png'
    WHEN LOWER(name) = 'choconut chip' THEN '/images/menu-items/choconut-chip.png'
    WHEN LOWER(name) = 'cookie jar special' THEN '/images/menu-items/og-chip.png'
    WHEN LOWER(name) = 'semi sweet delight' THEN '/images/menu-items/sw-chip.png'
    WHEN LOWER(name) = 'biscoff dreams' THEN '/images/menu-items/biscoff-chip.png'
    WHEN LOWER(name) = 'oreo madness' THEN '/images/menu-items/oreo-dunk-chip.png'
    ELSE image_url
END
WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys');

-- Create an index on image_url for performance
CREATE INDEX IF NOT EXISTS idx_menu_items_image_url ON menu_items(image_url);

-- Add a function to get restaurant theme
CREATE OR REPLACE FUNCTION get_restaurant_theme(restaurant_slug VARCHAR)
RETURNS JSON AS $$
BEGIN
    RETURN (
        SELECT theme_config 
        FROM restaurants 
        WHERE slug = restaurant_slug
    );
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON COLUMN restaurants.theme_config IS 'JSON configuration for restaurant-specific theme colors and gradients';
COMMENT ON COLUMN menu_items.image_url IS 'URL or path to menu item image';

-- Migration completed successfully
SELECT 'Migration 002_add_restaurant_theme_and_images.sql completed successfully' AS status;