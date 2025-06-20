-- Load Cookie Shop sample data into the database
-- This script creates The Cookie Jar restaurant with full menu and ingredients

-- Insert The Cookie Jar restaurant
INSERT INTO restaurants (id, name, slug, cuisine_type, description, avatar_config, contact_info, settings, is_active) VALUES 
(
    'bd1ea262-010a-46d1-9a39-4f3daf09fb29',
    'The Cookie Jar',
    'the-cookie-jar',
    'Dessert',
    'Gourmet warm cookies made fresh daily with premium ingredients',
    '{
        "name": "Baker Betty",
        "personality": "friendly_knowledgeable",
        "greeting": "Welcome to The Cookie Jar! I''m Baker Betty, and I''m here to help you find your perfect warm cookie. What kind of sweet treat are you craving today?",
        "tone": "warm",
        "special_instructions": "Always emphasize the warmth and freshness of cookies, mention that they''re made to order, and suggest milk pairings"
    }',
    '{
        "phone": "(555) 123-4567",
        "email": "hello@thecookiejar.com",
        "address": "123 Sweet Street, Dessert City, DC 12345"
    }',
    '{
        "business_hours": {
            "monday": "10:00 AM - 10:00 PM",
            "tuesday": "10:00 AM - 10:00 PM",
            "wednesday": "10:00 AM - 10:00 PM",
            "thursday": "10:00 AM - 10:00 PM",
            "friday": "10:00 AM - 11:00 PM",
            "saturday": "10:00 AM - 11:00 PM",
            "sunday": "11:00 AM - 9:00 PM"
        },
        "order_types": ["dine-in", "takeout", "delivery"],
        "primary_color": "#8B4513",
        "accent_color": "#D2691E"
    }',
    true
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    avatar_config = EXCLUDED.avatar_config,
    contact_info = EXCLUDED.contact_info,
    settings = EXCLUDED.settings;

-- Insert menu categories
INSERT INTO menu_categories (id, restaurant_id, name, description, display_order, is_active) VALUES 
('33fa5974-1667-4f7c-872c-a70f0960a505', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', 'Signature Cookies', 'Our classic warm gourmet cookies', 1, true),
('3760dd64-a7fd-4692-b4a2-bdf6c8276f9b', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', 'Specialty Cookies', 'Unique creations with special toppings and infusions', 2, true),
('07ef8bd0-b2d3-48e4-95f8-ca9f092dc388', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', 'Beverages', 'Perfect pairings for your cookies', 3, true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    display_order = EXCLUDED.display_order;

-- Insert ingredients
INSERT INTO ingredients (id, name, category, allergen_info) VALUES 
-- Base baking ingredients
('11111111-1111-1111-1111-111111111001', 'Unsalted AA butter', 'Dairy', '["dairy"]'),
('11111111-1111-1111-1111-111111111002', 'White granulated sugar', 'Sweetener', '[]'),
('11111111-1111-1111-1111-111111111003', 'Brown sugar', 'Sweetener', '[]'),
('11111111-1111-1111-1111-111111111004', 'Liquid egg', 'Protein', '["eggs"]'),
('11111111-1111-1111-1111-111111111005', 'Vanilla extract', 'Flavoring', '[]'),
('11111111-1111-1111-1111-111111111006', 'Flour', 'Grain', '["gluten"]'),
('11111111-1111-1111-1111-111111111007', 'Baking powder', 'Leavening', '[]'),
('11111111-1111-1111-1111-111111111008', 'Salt', 'Seasoning', '[]'),
('11111111-1111-1111-1111-111111111009', 'Vegetable shortening', 'Fat', '[]'),
('11111111-1111-1111-1111-111111111010', 'Almond extract', 'Flavoring', '["tree_nuts"]'),

-- Chocolate varieties
('11111111-1111-1111-1111-111111111011', 'Milk chocolate chips', 'Chocolate', '["dairy"]'),
('11111111-1111-1111-1111-111111111012', 'Semi-sweet chocolate wafers', 'Chocolate', '["dairy"]'),
('11111111-1111-1111-1111-111111111013', 'White chocolate chips', 'Chocolate', '["dairy"]'),
('11111111-1111-1111-1111-111111111014', 'Cocoa powder', 'Chocolate', '[]'),

-- Biscoff ingredients
('11111111-1111-1111-1111-111111111015', 'Biscoff cookie crumbs', 'Cookie', '["gluten"]'),
('11111111-1111-1111-1111-111111111016', 'Biscoff cookie butter', 'Spread', '["gluten"]'),

-- Toppings and mix-ins
('11111111-1111-1111-1111-111111111017', 'Sea salt', 'Seasoning', '[]'),
('11111111-1111-1111-1111-111111111018', 'Caramel', 'Topping', '["dairy"]'),
('11111111-1111-1111-1111-111111111019', 'Toffee bits', 'Topping', '["dairy"]'),
('11111111-1111-1111-1111-111111111020', 'Sweetened condensed milk', 'Dairy', '["dairy"]'),
('11111111-1111-1111-1111-111111111021', 'Crushed Oreos', 'Cookie', '["gluten"]'),
('11111111-1111-1111-1111-111111111022', 'Cinnamon sugar', 'Topping', '[]'),
('11111111-1111-1111-1111-111111111023', 'Toasted coconut', 'Topping', '["tree_nuts"]'),
('11111111-1111-1111-1111-111111111024', 'Pistachio cream', 'Nut Spread', '["tree_nuts"]'),
('11111111-1111-1111-1111-111111111025', 'Kataifi', 'Pastry', '["gluten"]'),
('11111111-1111-1111-1111-111111111026', 'Confetti sprinkles', 'Topping', '[]'),

-- Modifier ingredients (Cream Cheese Frosting)
('11111111-1111-1111-1111-111111111027', 'Cream cheese', 'Dairy', '["dairy"]'),
('11111111-1111-1111-1111-111111111028', 'White sugar', 'Sweetener', '[]'),

-- Modifier ingredients (Whipped Topping)
('11111111-1111-1111-1111-111111111029', 'Whipped Topping', 'Topping', '["dairy"]'),

-- Beverage ingredients
('11111111-1111-1111-1111-111111111030', 'Whole milk', 'Dairy', '["dairy"]'),
('11111111-1111-1111-1111-111111111031', 'Chocolate syrup', 'Flavoring', '[]'),
('11111111-1111-1111-1111-111111111032', 'Fresh brewed coffee', 'Beverage', '[]'),
('11111111-1111-1111-1111-111111111033', 'Vanilla ice cream', 'Dairy', '["dairy"]')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    allergen_info = EXCLUDED.allergen_info;

-- Insert Signature Cookies
INSERT INTO menu_items (id, restaurant_id, category_id, name, description, price, is_available, is_signature, spice_level, preparation_time, allergen_info, tags, display_order) VALUES 
('22222222-2222-2222-2222-222222222001', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '33fa5974-1667-4f7c-872c-a70f0960a505', 'Boneless', 'Our original signature warm gourmet cookie with a perfectly balanced buttery flavor.', 3.99, true, false, 0, 12, '["dairy", "eggs", "gluten"]', '["warm", "fresh-baked", "gourmet"]', 1),

('22222222-2222-2222-2222-222222222002', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '33fa5974-1667-4f7c-872c-a70f0960a505', 'OG', 'Our signature warm gourmet chocolate chip cookie.', 4.49, true, false, 0, 12, '["dairy", "eggs", "gluten"]', '["warm", "fresh-baked", "gourmet"]', 2),

('22222222-2222-2222-2222-222222222003', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '33fa5974-1667-4f7c-872c-a70f0960a505', 'Biscoff', 'A warm gourmet chip cookie made with Biscoff cookie crumbs, white chocolate chips, and stuffed with Biscoff cookie butter.', 5.49, true, true, 0, 15, '["dairy", "eggs", "gluten"]', '["warm", "fresh-baked", "gourmet"]', 3),

('22222222-2222-2222-2222-222222222004', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '33fa5974-1667-4f7c-872c-a70f0960a505', 'Semi Sweet', 'A warm gourmet cookie made with semi-sweet chocolate wafers and topped with Maldon sea salt.', 4.99, true, false, 0, 12, '["dairy", "eggs", "gluten"]', '["warm", "fresh-baked", "gourmet"]', 4),

('22222222-2222-2222-2222-222222222005', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '33fa5974-1667-4f7c-872c-a70f0960a505', 'Cocoa', 'A warm gourmet cocoa cookie made with rich Belgian cocoa powder.', 4.49, true, false, 0, 12, '["dairy", "eggs", "gluten"]', '["warm", "fresh-baked", "gourmet"]', 5),

('22222222-2222-2222-2222-222222222006', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '33fa5974-1667-4f7c-872c-a70f0960a505', 'Sugar Cookie', 'Our signature sugar cookie topped with house-made cream cheese frosting and confetti sprinkles.', 4.99, true, false, 0, 15, '["dairy", "eggs", "gluten", "tree_nuts"]', '["warm", "fresh-baked", "gourmet"]', 6)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    preparation_time = EXCLUDED.preparation_time,
    allergen_info = EXCLUDED.allergen_info;

-- Insert Specialty Cookies
INSERT INTO menu_items (id, restaurant_id, category_id, name, description, price, is_available, is_signature, spice_level, preparation_time, allergen_info, tags, display_order) VALUES 
('22222222-2222-2222-2222-222222222007', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '3760dd64-a7fd-4692-b4a2-bdf6c8276f9b', 'Better Than Sex Chip', 'Base cocoa cookie infused with caramel, and topped with whipped topping, more caramel, and toffee bits', 6.99, true, true, 0, 18, '["dairy", "eggs", "gluten"]', '["specialty", "gourmet", "indulgent"]', 1),

('22222222-2222-2222-2222-222222222008', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '3760dd64-a7fd-4692-b4a2-bdf6c8276f9b', 'Oreo Dunk Chip', 'A rich cocoa cookie infused with sweetened condensed milk and topped with white chocolate and crushed Oreos', 6.49, true, false, 0, 18, '["dairy", "eggs", "gluten"]', '["specialty", "gourmet", "indulgent"]', 2),

('22222222-2222-2222-2222-222222222009', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '3760dd64-a7fd-4692-b4a2-bdf6c8276f9b', 'Tres Leches Chip', 'A warm gourmet buttery cookie infused with sweetened condensed milk and topped with whipped topping and cinnamon sugar', 6.49, true, false, 0, 18, '["dairy", "eggs", "gluten"]', '["specialty", "gourmet", "indulgent"]', 3),

('22222222-2222-2222-2222-222222222010', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '3760dd64-a7fd-4692-b4a2-bdf6c8276f9b', 'Choconut Chip', 'A warm OG chip capped with melted milk chocolate and topped with fresh toasted coconut', 6.99, true, false, 0, 20, '["dairy", "eggs", "gluten", "tree_nuts"]', '["specialty", "gourmet", "indulgent"]', 4),

('22222222-2222-2222-2222-222222222011', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '3760dd64-a7fd-4692-b4a2-bdf6c8276f9b', 'Dubai Chocolate Pistachio Cream', 'A cocoa cookie infused with pistachio cream and kataifi', 7.99, true, true, 0, 20, '["dairy", "eggs", "gluten", "tree_nuts"]', '["specialty", "gourmet", "indulgent"]', 5)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    preparation_time = EXCLUDED.preparation_time,
    allergen_info = EXCLUDED.allergen_info;

-- Insert Beverages
INSERT INTO menu_items (id, restaurant_id, category_id, name, description, price, is_available, is_signature, spice_level, preparation_time, allergen_info, tags, display_order) VALUES 
('22222222-2222-2222-2222-222222222012', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '07ef8bd0-b2d3-48e4-95f8-ca9f092dc388', 'Fresh Milk', 'Ice cold whole milk - the perfect cookie companion', 2.99, true, false, 0, 1, '["dairy"]', '["beverage", "drink"]', 1),

('22222222-2222-2222-2222-222222222013', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '07ef8bd0-b2d3-48e4-95f8-ca9f092dc388', 'Chocolate Milk', 'Rich chocolate milk made with premium chocolate syrup', 3.49, true, false, 0, 2, '["dairy"]', '["beverage", "drink"]', 2),

('22222222-2222-2222-2222-222222222014', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '07ef8bd0-b2d3-48e4-95f8-ca9f092dc388', 'Cookie Milkshake', 'Vanilla milkshake blended with your choice of cookie', 5.99, true, false, 0, 5, '["dairy"]', '["beverage", "drink"]', 3),

('22222222-2222-2222-2222-222222222015', 'bd1ea262-010a-46d1-9a39-4f3daf09fb29', '07ef8bd0-b2d3-48e4-95f8-ca9f092dc388', 'Hot Coffee', 'Fresh brewed coffee - great with our chocolate cookies', 2.49, true, false, 0, 3, '[]', '["beverage", "drink"]', 4)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    preparation_time = EXCLUDED.preparation_time,
    allergen_info = EXCLUDED.allergen_info;

-- Insert menu item ingredients relationships
-- Boneless cookie ingredients (base recipe)
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, true), -- Liquid egg
('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222001', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false) -- Baking powder
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- OG cookie ingredients
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111011', '1', 'portion', false, true), -- Milk chocolate chips
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, false), -- Liquid egg
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222002', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false) -- Baking powder
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Biscoff cookie ingredients
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111013', '1', 'portion', false, true), -- White chocolate chips
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111015', '1', 'portion', false, true), -- Biscoff cookie crumbs
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111016', '1', 'portion', false, true), -- Biscoff cookie butter
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, false), -- Liquid egg
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222003', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false) -- Baking powder
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Semi Sweet cookie ingredients
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111012', '1', 'portion', false, true), -- Semi-sweet chocolate wafers
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, false), -- Liquid egg
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
('22222222-2222-2222-2222-222222222004', '11111111-1111-1111-1111-111111111017', '1', 'portion', false, false) -- Sea salt (topping)
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Cocoa cookie ingredients (base for several specialty cookies)
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, true), -- Liquid egg
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
('22222222-2222-2222-2222-222222222005', '11111111-1111-1111-1111-111111111014', '1', 'portion', false, true) -- Cocoa powder
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Sugar Cookie ingredients
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111009', '1', 'portion', false, true), -- Vegetable shortening
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111028', '1', 'portion', false, true), -- White sugar
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, true), -- Liquid eggs
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111010', '1', 'portion', false, false), -- Almond extract
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111008', '1', 'portion', false, false), -- Salt
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
-- Cream cheese frosting components
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111027', '1', 'portion', false, false), -- Cream cheese
('22222222-2222-2222-2222-222222222006', '11111111-1111-1111-1111-111111111026', '1', 'portion', false, false) -- Confetti sprinkles
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Better Than Sex Chip ingredients (cocoa base + additions)
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
-- Cocoa base ingredients
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, true), -- Liquid egg
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111014', '1', 'portion', false, true), -- Cocoa powder
-- Specialty additions
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111018', '1', 'portion', false, true), -- Caramel
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111019', '1', 'portion', false, true), -- Toffee bits
('22222222-2222-2222-2222-222222222007', '11111111-1111-1111-1111-111111111029', '1', 'portion', false, true) -- Whipped Topping
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Oreo Dunk Chip ingredients (cocoa base + additions)
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
-- Cocoa base ingredients
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, true), -- Liquid egg
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111014', '1', 'portion', false, true), -- Cocoa powder
-- Specialty additions
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111020', '1', 'portion', false, true), -- Sweetened condensed milk
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111013', '1', 'portion', false, true), -- White chocolate
('22222222-2222-2222-2222-222222222008', '11111111-1111-1111-1111-111111111021', '1', 'portion', false, true) -- Crushed Oreos
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Tres Leches Chip ingredients (boneless base + additions)
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
-- Boneless base ingredients
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, true), -- Liquid egg
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
-- Specialty additions
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111020', '1', 'portion', false, true), -- Sweetened condensed milk
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111022', '1', 'portion', false, true), -- Cinnamon sugar
('22222222-2222-2222-2222-222222222009', '11111111-1111-1111-1111-111111111029', '1', 'portion', false, true) -- Whipped Topping
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Choconut Chip ingredients (OG base + additions)
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
-- OG base ingredients
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111011', '1', 'portion', false, true), -- Milk chocolate chips
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, false), -- Liquid egg
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
-- Specialty additions
('22222222-2222-2222-2222-222222222010', '11111111-1111-1111-1111-111111111023', '1', 'portion', false, true) -- Toasted coconut
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Dubai Chocolate Pistachio Cream ingredients (cocoa base + additions)
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
-- Cocoa base ingredients
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111001', '1', 'portion', false, true), -- Unsalted AA butter
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111002', '1', 'portion', false, true), -- White granulated sugar
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111003', '1', 'portion', false, true), -- Brown sugar
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111004', '1', 'portion', false, true), -- Liquid egg
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111005', '1', 'portion', false, false), -- Vanilla extract
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111006', '1', 'portion', false, false), -- Flour
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111007', '1', 'portion', false, false), -- Baking powder
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111014', '1', 'portion', false, true), -- Cocoa powder
-- Specialty additions
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111024', '1', 'portion', false, true), -- Pistachio cream
('22222222-2222-2222-2222-222222222011', '11111111-1111-1111-1111-111111111025', '1', 'portion', false, true) -- Kataifi
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Fresh Milk beverage
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222012', '11111111-1111-1111-1111-111111111030', '1', 'serving', false, true)
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Chocolate Milk beverage
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222013', '11111111-1111-1111-1111-111111111030', '1', 'serving', false, true), -- Whole milk
('22222222-2222-2222-2222-222222222013', '11111111-1111-1111-1111-111111111031', '1', 'serving', false, true) -- Chocolate syrup
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Cookie Milkshake beverage
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222014', '11111111-1111-1111-1111-111111111030', '1', 'serving', false, true), -- Whole milk
('22222222-2222-2222-2222-222222222014', '11111111-1111-1111-1111-111111111033', '1', 'serving', false, true) -- Vanilla ice cream
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Hot Coffee beverage
INSERT INTO menu_item_ingredients (menu_item_id, ingredient_id, quantity, unit, is_optional, is_primary) VALUES 
('22222222-2222-2222-2222-222222222015', '11111111-1111-1111-1111-111111111032', '1', 'serving', false, true) -- Fresh brewed coffee
ON CONFLICT (menu_item_id, ingredient_id) DO NOTHING;

-- Display success message
DO $$
BEGIN
    RAISE NOTICE '🍪 Successfully loaded The Cookie Jar restaurant data!';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - 1 restaurant (The Cookie Jar)';
    RAISE NOTICE '  - 3 menu categories';
    RAISE NOTICE '  - 33 ingredients';
    RAISE NOTICE '  - 15 menu items (6 signature + 5 specialty + 4 beverages)';
    RAISE NOTICE '  - Ingredient relationships for key items';
    RAISE NOTICE '';
    RAISE NOTICE '🌐 Visit http://localhost:3000/r/the-cookie-jar to see your cookie shop!';
END $$;