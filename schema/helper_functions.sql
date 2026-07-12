-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Automatically add items to shopping list when pantry falls below threshold
-- This should be called after pantry quantities are updated
CREATE OR REPLACE FUNCTION check_and_add_to_shopping_list()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if any pantry items are now below their stock threshold
  INSERT INTO shopping_list_items (household_id, item_id, quantity, created_at, updated_at)
  SELECT 
    pi.household_id,
    pi.item_id,
    (pst.threshold_quantity - pi.quantity) AS quantity,
    NOW(),
    NOW()
  FROM pantry_items pi
  JOIN pantry_stock_thresholds pst ON pi.household_id = pst.household_id AND pi.item_id = pst.item_id
  WHERE pi.household_id = NEW.household_id
    AND pi.item_id = NEW.item_id
    AND pi.quantity < pst.threshold_quantity
    AND NOT EXISTS (
      SELECT 1 FROM shopping_list_items sli 
      WHERE sli.household_id = pi.household_id AND sli.item_id = pi.item_id
    )
  ON CONFLICT (household_id, item_id) DO UPDATE SET
    quantity = EXCLUDED.quantity,
    updated_at = NOW();

  -- Track the source of this shopping list addition
  INSERT INTO shopping_list_item_sources (shopping_list_item_id, source_type, quantity_added, created_at)
  SELECT 
    sli.id,
    'stock_threshold',
    (pst.threshold_quantity - NEW.quantity),
    NOW()
  FROM shopping_list_items sli
  JOIN pantry_stock_thresholds pst ON sli.household_id = pst.household_id AND sli.item_id = pst.item_id
  WHERE sli.household_id = NEW.household_id
    AND sli.item_id = NEW.item_id
    AND NEW.quantity < pst.threshold_quantity
    AND NOT EXISTS (
      SELECT 1 FROM shopping_list_item_sources slis
      WHERE slis.shopping_list_item_id = sli.id AND slis.source_type = 'stock_threshold'
    );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_stock_threshold
AFTER UPDATE ON pantry_items
FOR EACH ROW
EXECUTE FUNCTION check_and_add_to_shopping_list();

-- Function: Add items to shopping list when a meal is planned
-- Call this function when a new meal plan is created
CREATE OR REPLACE FUNCTION add_meal_ingredients_to_shopping_list(meal_plan_id BIGINT)
RETURNS VOID AS $$
DECLARE
  v_household_id BIGINT;
  v_meal_id BIGINT;
BEGIN
  -- Get household and meal IDs from meal plan
  SELECT household_id, meal_id INTO v_household_id, v_meal_id
  FROM meal_plans
  WHERE id = meal_plan_id;

  -- Add each ingredient to shopping list (or increment if already exists)
  INSERT INTO shopping_list_items (household_id, item_id, quantity, created_at, updated_at)
  SELECT 
    v_household_id,
    mi.item_id,
    mi.quantity,
    NOW(),
    NOW()
  FROM meal_ingredients mi
  WHERE mi.meal_id = v_meal_id
  ON CONFLICT (household_id, item_id) DO UPDATE SET
    quantity = shopping_list_items.quantity + EXCLUDED.quantity,
    updated_at = NOW();

  -- Track the source of these additions
  INSERT INTO shopping_list_item_sources (shopping_list_item_id, source_type, quantity_added, source_reference_id, created_at)
  SELECT 
    sli.id,
    'meal_plan',
    mi.quantity,
    meal_plan_id,
    NOW()
  FROM shopping_list_items sli
  JOIN meal_ingredients mi ON sli.item_id = mi.item_id
  WHERE sli.household_id = v_household_id
    AND mi.meal_id = v_meal_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Move shopping list items to pantry when shopping is completed
-- Call this function when a shopping list item is marked as purchased
CREATE OR REPLACE FUNCTION move_shopping_to_pantry(shopping_list_item_id BIGINT)
RETURNS VOID AS $$
DECLARE
  v_household_id BIGINT;
  v_item_id BIGINT;
  v_quantity DECIMAL;
BEGIN
  -- Get shopping list item details
  SELECT household_id, item_id, quantity 
  INTO v_household_id, v_item_id, v_quantity
  FROM shopping_list_items
  WHERE id = shopping_list_item_id;

  -- Add to pantry (or increment if already exists)
  INSERT INTO pantry_items (household_id, item_id, quantity, updated_at)
  VALUES (v_household_id, v_item_id, v_quantity, NOW())
  ON CONFLICT (household_id, item_id) DO UPDATE SET
    quantity = pantry_items.quantity + EXCLUDED.quantity,
    updated_at = NOW();

  -- Remove from shopping list
  DELETE FROM shopping_list_items WHERE id = shopping_list_item_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Deduct meal ingredients from pantry when meal is marked as prepared
-- Call this function when a meal plan is marked as is_prepared = true
CREATE OR REPLACE FUNCTION deduct_meal_from_pantry(meal_plan_id BIGINT)
RETURNS VOID AS $$
DECLARE
  v_meal_id BIGINT;
  v_household_id BIGINT;
BEGIN
  -- Get meal and household IDs
  SELECT meal_id, household_id INTO v_meal_id, v_household_id
  FROM meal_plans
  WHERE id = meal_plan_id;

  -- Deduct each ingredient from pantry
  UPDATE pantry_items pi
  SET quantity = quantity - mi.quantity,
      updated_at = NOW()
  FROM meal_ingredients mi
  WHERE pi.household_id = v_household_id
    AND pi.item_id = mi.item_id
    AND mi.meal_id = v_meal_id
    AND pi.quantity >= mi.quantity;

  -- Update the meal plan to track when it was prepared
  UPDATE meal_plans
  SET is_prepared = TRUE, prepared_at = NOW()
  WHERE id = meal_plan_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
