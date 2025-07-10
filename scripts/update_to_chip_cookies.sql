-- Update Baker Betty's to Chip Cookies completely
UPDATE restaurants 
SET 
    name = 'Chip Cookies',
    description = 'Handmade gourmet cookies with premium ingredients, baked fresh throughout the day',
    avatar_config = jsonb_set(
        jsonb_set(
            avatar_config::jsonb,
            '{name}',
            '"Cookie Expert Betty"'
        ),
        '{greeting}',
        '"Welcome to Chip Cookies! I''m Betty, your cookie expert. Our handmade gourmet cookies are baked fresh throughout the day. What delicious warm cookie can I help you discover today?"'
    )
WHERE slug = 'baker-bettys';

-- Update existing menu items with proper Chip Cookies menu
DELETE FROM menu_items WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys');
DELETE FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys');

-- Insert categories
INSERT INTO menu_categories (restaurant_id, name, description, display_order, is_active) VALUES
((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 'Classic Chips', 'Our signature gourmet cookie collection', 1, true),
((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 'Specialty Chips', 'Unique cookie creations with special toppings and fillings', 2, true),
((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 'Beverages', 'Perfect pairings for your warm cookies', 3, true);

-- Insert menu items with proper image URLs
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
 'https://www.chipcookies.co/cdn/shop/files/chip_og-chip_small_db52d8f6-da87-47f0-b39f-3de088965c93.png?v=1729105762&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_sw-chip_small_95c00d2d-c3de-48e2-a8ef-e85c82bb0b3b.png?v=1729105750&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_sugar-chip_small_0cbdb3d2-3b44-446f-b7d7-5c088c09efbc.png?v=1729105823&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_cotw_smores-chip_small_8ecf8007-6649-415b-b286-0ca129379b06.png?v=1729105785&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_biscoff-chip_small_c8a1c46e-72ba-47fa-8f4e-c97ff11c5e0b.png?v=1729105739&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_bts-chip_small_f0f7f9cf-fca8-4d02-ad08-d7f088fe7f22.png?v=1729105797&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_tres-leches-chip_small_3e916f76-d4f2-4c9e-a04d-ce9d87f2c7e9.png?v=1729105810&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_oreo-dunk-chip_small_e33e4a23-10f4-4ff8-9d08-f967b32e19ba.png?v=1729105774&width=480'),

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
 'https://www.chipcookies.co/cdn/shop/files/chip_cotw_chocochip_small.png?v=1735060989&width=480'),

-- Beverages
((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Beverages'),
 'Cold Milk', 
 'Ice-cold whole milk - the classic cookie companion',
 3.00,
 ARRAY['dairy'],
 ARRAY['vegetarian', 'gluten_free'],
 false,
 true,
 1,
 NULL),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Beverages'),
 'Chocolate Milk', 
 'Rich and creamy chocolate milk',
 3.50,
 ARRAY['dairy'],
 ARRAY['vegetarian', 'gluten_free'],
 false,
 true,
 2,
 NULL),

((SELECT id FROM restaurants WHERE slug = 'baker-bettys'), 
 (SELECT id FROM menu_categories WHERE restaurant_id = (SELECT id FROM restaurants WHERE slug = 'baker-bettys') AND name = 'Beverages'),
 'Oat Milk', 
 'Creamy oat milk for our dairy-free friends',
 3.50,
 ARRAY[],
 ARRAY['vegan', 'gluten_free', 'dairy_free'],
 false,
 true,
 3,
 NULL);