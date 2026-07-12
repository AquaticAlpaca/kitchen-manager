-- ============================================================================
-- RLS POLICIES (Row-Level Security)
-- ============================================================================
-- Enable RLS for all tables to ensure data isolation between households

ALTER TABLE households ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE pantry_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE pantry_stock_thresholds ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_list_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_list_item_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_plans ENABLE ROW LEVEL SECURITY;

-- Policies ensure users can only access data from their own household
-- NOTE: These are template policies. Adjust auth.uid() to match your Supabase auth setup.

CREATE POLICY "Users can view their own household" ON households
  FOR SELECT USING (
    id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY "Users can view household members" ON users
  FOR SELECT USING (
    household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY "Users can view items in their household" ON items
  FOR SELECT USING (
    household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY "Users can view pantry items in their household" ON pantry_items
  FOR SELECT USING (
    household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY "Users can view stock thresholds in their household" ON pantry_stock_thresholds
  FOR SELECT USING (
    household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY "Users can view shopping list items in their household" ON shopping_list_items
  FOR SELECT USING (
    household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY "Users can view shopping list item sources in their household" ON shopping_list_item_sources
  FOR SELECT USING (
    shopping_list_item_id IN (
      SELECT id FROM shopping_list_items 
      WHERE household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
    )
  );

CREATE POLICY "Users can view meals in their household" ON meals
  FOR SELECT USING (
    household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

CREATE POLICY "Users can view meal ingredients in their household" ON meal_ingredients
  FOR SELECT USING (
    meal_id IN (
      SELECT id FROM meals 
      WHERE household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
    )
  );

CREATE POLICY "Users can view meal plans in their household" ON meal_plans
  FOR SELECT USING (
    household_id IN (SELECT household_id FROM users WHERE id = auth.uid())
  );

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
