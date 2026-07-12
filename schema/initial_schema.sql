-- ============================================================================
-- Kitchen Management App Schema
-- For: Senior-friendly Kitchen Management Application
-- Database: PostgreSQL via Supabase
-- ============================================================================

-- ============================================================================
-- TABLES: Core Domain Models
-- ============================================================================

-- Households: Top-level container for users and all their kitchen data
CREATE TABLE households (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  unit_system VARCHAR(20) NOT NULL CHECK (unit_system IN ('imperial', 'metric')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Users: Members of a household
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  is_owner BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_household_id ON users(household_id);

-- ============================================================================
-- TABLES: Unit System & Conversion
-- ============================================================================

-- Canonical units: How items are sold in stores
-- Examples: "pound", "liter", "bunch", "count", etc.
CREATE TABLE canonical_units (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  abbreviation VARCHAR(10) NOT NULL UNIQUE,
  unit_system VARCHAR(20) NOT NULL CHECK (unit_system IN ('imperial', 'metric', 'universal')),
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Cooking units: Units used in recipes
-- Examples: "cup", "tablespoon", "teaspoon", "gram", "ml", etc.
CREATE TABLE cooking_units (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  abbreviation VARCHAR(10) NOT NULL UNIQUE,
  unit_system VARCHAR(20) NOT NULL CHECK (unit_system IN ('imperial', 'metric', 'universal')),
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Conversion factors: How to convert between canonical and cooking units
-- Example: "1 cup flour" = "125 grams flour"
-- Requires ingredient specificity because density varies by ingredient
CREATE TABLE unit_conversions (
  id BIGSERIAL PRIMARY KEY,
  ingredient_name VARCHAR(255) NOT NULL,
  canonical_unit_id BIGINT NOT NULL REFERENCES canonical_units(id),
  cooking_unit_id BIGINT NOT NULL REFERENCES cooking_units(id),
  canonical_quantity DECIMAL(10, 3) NOT NULL,
  cooking_quantity DECIMAL(10, 3) NOT NULL,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(ingredient_name, canonical_unit_id, cooking_unit_id)
);

CREATE INDEX idx_unit_conversions_ingredient ON unit_conversions(ingredient_name);
CREATE INDEX idx_unit_conversions_canonical ON unit_conversions(canonical_unit_id);
CREATE INDEX idx_unit_conversions_cooking ON unit_conversions(cooking_unit_id);

-- ============================================================================
-- TABLES: Items (Grocery/Household Items)
-- ============================================================================

-- Items: The basic unit of data; represents a grocery/household item
-- Scoped to household (phase 1: no global item database)
CREATE TABLE items (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  canonical_unit_id BIGINT NOT NULL REFERENCES canonical_units(id),
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(household_id, name)
);

CREATE INDEX idx_items_household_id ON items(household_id);
CREATE INDEX idx_items_canonical_unit_id ON items(canonical_unit_id);

-- ============================================================================
-- TABLES: Pantry (Source of Truth)
-- ============================================================================

-- Pantry items: Current inventory of items in pantry/fridge/freezer
-- This is the source of truth; all other features modify this
CREATE TABLE pantry_items (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  quantity DECIMAL(10, 3) NOT NULL DEFAULT 0 CHECK (quantity >= 0),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(household_id, item_id)
);

CREATE INDEX idx_pantry_items_household_id ON pantry_items(household_id);
CREATE INDEX idx_pantry_items_item_id ON pantry_items(item_id);

-- Pantry stock thresholds: Automatic reordering configuration
-- When a pantry item quantity falls below this threshold, it's added to shopping list
CREATE TABLE pantry_stock_thresholds (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  threshold_quantity DECIMAL(10, 3) NOT NULL CHECK (threshold_quantity >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(household_id, item_id)
);

CREATE INDEX idx_stock_thresholds_household_id ON pantry_stock_thresholds(household_id);

-- ============================================================================
-- TABLES: Shopping List
-- ============================================================================

-- Shopping list items: Aggregated list of items to purchase
-- Quantity combines manual additions and automatic system additions
CREATE TABLE shopping_list_items (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  quantity DECIMAL(10, 3) NOT NULL DEFAULT 0 CHECK (quantity > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(household_id, item_id)
);

CREATE INDEX idx_shopping_list_household_id ON shopping_list_items(household_id);
CREATE INDEX idx_shopping_list_item_id ON shopping_list_items(item_id);

-- Shopping list item sources: Track where each item came from (for reference/debugging)
CREATE TABLE shopping_list_item_sources (
  id BIGSERIAL PRIMARY KEY,
  shopping_list_item_id BIGINT NOT NULL REFERENCES shopping_list_items(id) ON DELETE CASCADE,
  source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('manual', 'meal_plan', 'stock_threshold')),
  quantity_added DECIMAL(10, 3) NOT NULL,
  source_reference_id BIGINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_shopping_item_sources_shopping_id ON shopping_list_item_sources(shopping_list_item_id);

-- ============================================================================
-- TABLES: Meals & Recipes
-- ============================================================================

-- Meals: Collections of ingredients that can be scheduled or stored as recipes
-- Scoped to household; can be reused in multiple meal plans
CREATE TABLE meals (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(household_id, name)
);

CREATE INDEX idx_meals_household_id ON meals(household_id);

-- Meal ingredients: Specific quantities of items that compose a meal
-- Uses cooking units (e.g., "1 cup flour" not "0.22 pounds flour")
CREATE TABLE meal_ingredients (
  id BIGSERIAL PRIMARY KEY,
  meal_id BIGINT NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
  item_id BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  quantity DECIMAL(10, 3) NOT NULL CHECK (quantity > 0),
  cooking_unit_id BIGINT NOT NULL REFERENCES cooking_units(id),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_meal_ingredients_meal_id ON meal_ingredients(meal_id);
CREATE INDEX idx_meal_ingredients_item_id ON meal_ingredients(item_id);

-- ============================================================================
-- TABLES: Meal Planning
-- ============================================================================

-- Meal plans: Schedule meals for specific dates
-- A meal can appear multiple times on different dates
CREATE TABLE meal_plans (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  meal_id BIGINT NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
  planned_date DATE NOT NULL,
  is_prepared BOOLEAN NOT NULL DEFAULT FALSE,
  prepared_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_meal_plans_household_id ON meal_plans(household_id);
CREATE INDEX idx_meal_plans_meal_id ON meal_plans(meal_id);
CREATE INDEX idx_meal_plans_planned_date ON meal_plans(planned_date);
CREATE INDEX idx_meal_plans_is_prepared ON meal_plans(is_prepared);

-- ============================================================================
-- SAMPLE DATA: Canonical Units
-- ============================================================================

-- Common canonical (store) units - Imperial
INSERT INTO canonical_units (name, abbreviation, unit_system, description) VALUES
  ('pound', 'lb', 'imperial', 'Pound (weight)'),
  ('ounce', 'oz', 'imperial', 'Ounce (weight)'),
  ('gallon', 'gal', 'imperial', 'Gallon (volume)'),
  ('quart', 'qt', 'imperial', 'Quart (volume)'),
  ('pint', 'pt', 'imperial', 'Pint (volume)'),
  ('cup', 'cup', 'imperial', 'Cup (volume) - NOTE: as sold, not cooking unit'),
  ('fluid_ounce', 'fl oz', 'imperial', 'Fluid ounce (volume)');

-- Common canonical (store) units - Metric
INSERT INTO canonical_units (name, abbreviation, unit_system, description) VALUES
  ('kilogram', 'kg', 'metric', 'Kilogram (weight)'),
  ('gram', 'g', 'metric', 'Gram (weight)'),
  ('liter', 'L', 'metric', 'Liter (volume)'),
  ('milliliter', 'mL', 'metric', 'Milliliter (volume)');

-- Universal canonical units (same in both systems)
INSERT INTO canonical_units (name, abbreviation, unit_system, description) VALUES
  ('count', 'ct', 'universal', 'Whole items (eggs, apples, carrots, etc.)'),
  ('bunch', 'bunch', 'universal', 'Bunch (spinach, herbs, etc.)'),
  ('package', 'pkg', 'universal', 'Package'),
  ('box', 'box', 'universal', 'Box'),
  ('can', 'can', 'universal', 'Can'),
  ('jar', 'jar', 'universal', 'Jar');

-- ============================================================================
-- SAMPLE DATA: Cooking Units
-- ============================================================================

-- Common cooking units - Imperial
INSERT INTO cooking_units (name, abbreviation, unit_system, description) VALUES
  ('teaspoon', 'tsp', 'imperial', 'Teaspoon'),
  ('tablespoon', 'tbsp', 'imperial', 'Tablespoon'),
  ('fluid_ounce', 'fl oz', 'imperial', 'Fluid ounce'),
  ('cup', 'cup', 'imperial', 'Cup'),
  ('pint', 'pt', 'imperial', 'Pint'),
  ('quart', 'qt', 'imperial', 'Quart'),
  ('gallon', 'gal', 'imperial', 'Gallon'),
  ('pound', 'lb', 'imperial', 'Pound'),
  ('ounce', 'oz', 'imperial', 'Ounce');

-- Common cooking units - Metric
INSERT INTO cooking_units (name, abbreviation, unit_system, description) VALUES
  ('milliliter', 'mL', 'metric', 'Milliliter'),
  ('liter', 'L', 'metric', 'Liter'),
  ('gram', 'g', 'metric', 'Gram'),
  ('kilogram', 'kg', 'metric', 'Kilogram');

-- Universal cooking units
INSERT INTO cooking_units (name, abbreviation, unit_system, description) VALUES
  ('count', 'ct', 'universal', 'Whole items'),
  ('bunch', 'bunch', 'universal', 'Bunch');

-- ============================================================================
-- SAMPLE DATA: Unit Conversions
-- ============================================================================

-- Common cooking ingredient conversions (Imperial)
-- Source: NIST Metric Kitchen, Wikipedia Cooking Weights and Measures

-- Flour conversions (Imperial: pounds to cups)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('flour', 
  (SELECT id FROM canonical_units WHERE name = 'pound'), 
  (SELECT id FROM cooking_units WHERE name = 'cup'), 
  1, 3.6, 'All-purpose flour, approximate');

-- Milk conversions (Imperial: gallons to cups)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('milk', 
  (SELECT id FROM canonical_units WHERE name = 'gallon'), 
  (SELECT id FROM cooking_units WHERE name = 'cup'), 
  1, 16, 'Standard conversion');

-- Sugar conversions (Imperial: pound to cups)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('sugar', 
  (SELECT id FROM canonical_units WHERE name = 'pound'), 
  (SELECT id FROM cooking_units WHERE name = 'cup'), 
  1, 2.2, 'Granulated sugar, approximate');

-- Butter conversions (Imperial: pound to cups)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('butter', 
  (SELECT id FROM canonical_units WHERE name = 'pound'), 
  (SELECT id FROM cooking_units WHERE name = 'cup'), 
  1, 2, 'Standard conversion');

-- Honey conversions (Imperial: pound to cup)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('honey', 
  (SELECT id FROM canonical_units WHERE name = 'pound'), 
  (SELECT id FROM cooking_units WHERE name = 'cup'), 
  1, 1.33, 'Approximate');

-- Common cooking ingredient conversions (Metric)

-- Flour conversions (Metric: kilogram to grams)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('flour', 
  (SELECT id FROM canonical_units WHERE name = 'kilogram'), 
  (SELECT id FROM cooking_units WHERE name = 'gram'), 
  1, 1000, 'Standard conversion');

-- Milk conversions (Metric: liter to milliliter)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('milk', 
  (SELECT id FROM canonical_units WHERE name = 'liter'), 
  (SELECT id FROM cooking_units WHERE name = 'milliliter'), 
  1, 1000, 'Standard conversion');

-- Sugar conversions (Metric: kilogram to gram)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('sugar', 
  (SELECT id FROM canonical_units WHERE name = 'kilogram'), 
  (SELECT id FROM cooking_units WHERE name = 'gram'), 
  1, 1000, 'Standard conversion');

-- Butter conversions (Metric: kilogram to gram)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('butter', 
  (SELECT id FROM canonical_units WHERE name = 'kilogram'), 
  (SELECT id FROM cooking_units WHERE name = 'gram'), 
  1, 1000, 'Standard conversion');

-- Honey conversions (Metric: kilogram to gram)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('honey', 
  (SELECT id FROM canonical_units WHERE name = 'kilogram'), 
  (SELECT id FROM cooking_units WHERE name = 'gram'), 
  1, 1000, 'Standard conversion');

-- Common cooking ingredient conversions (Universal)

-- Eggs (count)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('eggs', 
  (SELECT id FROM canonical_units WHERE name = 'count'), 
  (SELECT id FROM cooking_units WHERE name = 'count'), 
  1, 1, 'Eggs by count');

-- Spinach (bunch to bunch)
INSERT INTO unit_conversions (ingredient_name, canonical_unit_id, cooking_unit_id, canonical_quantity, cooking_quantity, notes)
VALUES ('spinach', 
  (SELECT id FROM canonical_units WHERE name = 'bunch'), 
  (SELECT id FROM cooking_units WHERE name = 'bunch'), 
  1, 1, 'Fresh spinach by bunch');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
