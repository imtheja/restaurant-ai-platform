-- Update Baker Betty's with Chip Cookies branding and menu
-- This updates the existing restaurant with proper colors and menu items

-- Update restaurant branding and colors
UPDATE restaurants 
SET 
    settings = jsonb_set(
        jsonb_set(
            jsonb_set(
                settings::jsonb,
                '{primary_color}',
                '"#aa8a40"'
            ),
            '{accent_color}',
            '"#ede7d4"'
        ),
        '{branding}',
        '{
            "logo_url": "/images/chip-cookies-logo.png",
            "background_color": "#ffffff",
            "text_color": "#333333",
            "style": "modern_minimal"
        }'::jsonb
    ),
    description = 'Handmade gourmet cookies with premium ingredients, baked fresh throughout the day'
WHERE slug = 'baker-bettys';

-- Update menu categories
UPDATE menu_categories 
SET name = 'Classic Chips', 
    description = 'Our signature gourmet cookie collection'
WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys')
AND name = 'Signature Cookies';

UPDATE menu_categories 
SET name = 'Specialty Chips', 
    description = 'Unique cookie creations with special toppings and fillings'
WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys')
AND name = 'Specialty Cookies';

-- Clear existing menu items to add new ones
DELETE FROM menu_items 
WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys');

-- Insert new menu items based on Chip Cookies
INSERT INTO menu_items (restaurant_id, category_id, name, description, price, allergen_info, dietary_info, is_signature, is_available, display_order, image_url) VALUES
-- Classic Chips
((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Classic Chips'),
 'OG Chip', 
 'Our signature milk chocolate chip cookie - the one that started it all. Made with premium butter, brown sugar, and chunks of Belgian milk chocolate',
 4.50,
 ARRAY['gluten', 'dairy', 'eggs'],
 ARRAY['vegetarian'],
 true,
 true,
 1,
 'https://www.chipcookies.co/cdn/shop/files/chip_og-chip_small.png'),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Classic Chips'),
 'SW Chip', 
 'Semi-sweet chocolate perfection topped with Maldon sea salt. A sophisticated balance of sweet and savory',
 4.50,
 ARRAY['gluten', 'dairy', 'eggs'],
 ARRAY['vegetarian'],
 true,
 true,
 2,
 'https://www.chipcookies.co/cdn/shop/files/chip_sw-chip_small.png'),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Classic Chips'),
 'Sugar Chip', 
 'Classic sugar cookie topped with our signature cream cheese frosting and festive sprinkles',
 4.50,
 ARRAY['gluten', 'dairy', 'eggs'],
 ARRAY['vegetarian'],
 false,
 true,
 3,
 'https://www.chipcookies.co/cdn/shop/files/chip_sugar-chip_small.png'),

-- Specialty Chips
((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Specialty Chips'),
 'S''mores Chip', 
 'Stuffed with graham crackers, toasted marshmallow, and melted milk chocolate - campfire memories in every bite',
 5.50,
 ARRAY['gluten', 'dairy', 'eggs'],
 ARRAY['vegetarian'],
 true,
 true,
 1,
 'https://www.chipcookies.co/cdn/shop/files/chip_cotw_smores-chip_small.png'),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Specialty Chips'),
 'Biscoff Chip', 
 'Made with crushed Biscoff cookies and swirled with creamy cookie butter for the ultimate indulgence',
 5.00,
 ARRAY['gluten', 'dairy', 'eggs', 'soy'],
 ARRAY['vegetarian'],
 true,
 true,
 2,
 'https://www.chipcookies.co/cdn/shop/files/chip_biscoff-chip_small.png'),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Specialty Chips'),
 'BTS Chip', 
 'Rich Dutch cocoa cookie with gooey caramel and sweetened condensed milk - behind the scenes perfection',
 5.00,
 ARRAY['gluten', 'dairy', 'eggs'],
 ARRAY['vegetarian'],
 false,
 true,
 3,
 'https://www.chipcookies.co/cdn/shop/files/chip_bts-chip_small.png'),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Specialty Chips'),
 'Tres Leches Chip', 
 'Butter cookie soaked with three milks - evaporated milk, condensed milk, and heavy cream',
 5.00,
 ARRAY['gluten', 'dairy', 'eggs'],
 ARRAY['vegetarian'],
 false,
 true,
 4,
 'https://www.chipcookies.co/cdn/shop/files/chip_tres-leches-chip_small.png'),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Specialty Chips'),
 'Oreo Dunk Chip', 
 'Dutch cocoa cookie loaded with crushed Oreos and white chocolate chunks',
 5.00,
 ARRAY['gluten', 'dairy', 'eggs', 'soy'],
 ARRAY['vegetarian'],
 false,
 true,
 5,
 'https://www.chipcookies.co/cdn/shop/files/chip_oreo-dunk-chip_small.png'),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Specialty Chips'),
 'Choconut Chip', 
 'Milk chocolate cookie topped with toasted coconut flakes - tropical paradise in cookie form',
 5.00,
 ARRAY['gluten', 'dairy', 'eggs', 'tree_nuts'],
 ARRAY['vegetarian'],
 false,
 true,
 6,
 'https://www.chipcookies.co/cdn/shop/files/chip_choconut-chip_small.png');

-- Add beverages category if it doesn't exist
INSERT INTO menu_categories (restaurant_id, name, description, display_order, is_active) 
VALUES (
    (SELECT id FROM restaurants WHERE slug = 'baker-bettys'),
    'Beverages',
    'Perfect pairings for your warm cookies',
    3,
    true
) ON CONFLICT DO NOTHING;

-- Add milk options
INSERT INTO menu_items (restaurant_id, category_id, name, description, price, allergen_info, dietary_info, is_available, display_order) VALUES
((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Beverages'),
 'Cold Milk', 
 'Ice-cold whole milk - the classic cookie companion',
 3.00,
 ARRAY['dairy'],
 ARRAY['vegetarian', 'gluten_free'],
 true,
 1),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Beverages'),
 'Chocolate Milk', 
 'Rich and creamy chocolate milk',
 3.50,
 ARRAY['dairy'],
 ARRAY['vegetarian', 'gluten_free'],
 true,
 2),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Beverages'),
 'Oat Milk', 
 'Creamy oat milk for our dairy-free friends',
 3.50,
 ARRAY[],
 ARRAY['vegan', 'gluten_free', 'dairy_free'],
 true,
 3);

-- Update AI configuration greeting to match brand
UPDATE restaurants 
SET avatar_config = jsonb_set(
    avatar_config::jsonb,
    '{greeting}',
    '"Welcome to Chip Cookies! I''m Baker Betty, your cookie expert. Our handmade gourmet cookies are baked fresh throughout the day. What delicious warm cookie can I help you discover today?"'
)
WHERE slug = 'baker-bettys';