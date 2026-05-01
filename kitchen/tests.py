from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import Ingredient, MealPlan, MealIngredient, ShoppingListItem, StockUpdate, ActiveMealSchedule
from .services import (
    calculate_new_stock,
    update_ingredient_stock,
    generate_shopping_list_items,
    get_low_stock_ingredients,
    schedule_meal
)

User = get_user_model()


class IngredientModelTests(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name="Chicken Breast",
            unit="lb",
            current_stock=Decimal("5.0"),
            minimum_stock=Decimal("2.0"),
            category="meat"
        )

    def test_needs_reorder_when_below_minimum(self):
        self.ingredient.current_stock = Decimal("1.0")
        self.ingredient.save()
        self.assertTrue(self.ingredient.needs_reorder)

    def test_no_reorder_when_above_minimum(self):
        self.assertFalse(self.ingredient.needs_reorder)


class ServiceLayerTests(TestCase):
    def setUp(self):
        self.chef = User.objects.create_user(
            username="chef",
            password="pass",
            role=User.Role.CHEF
        )
        self.ingredient = Ingredient.objects.create(
            name="Rice",
            unit="cup",
            current_stock=Decimal("10.0"),
            minimum_stock=Decimal("3.0"),
            category="pantry"
        )

    def test_calculate_new_stock_added(self):
        new_stock, change = calculate_new_stock(
            self.ingredient,
            StockUpdate.UpdateType.ADDED,
            Decimal("5.0")
        )
        self.assertEqual(new_stock, Decimal("15.0"))
        self.assertEqual(change, Decimal("5.0"))

    def test_calculate_new_stock_used(self):
        new_stock, change = calculate_new_stock(
            self.ingredient,
            StockUpdate.UpdateType.USED,
            Decimal("3.0")
        )
        self.assertEqual(new_stock, Decimal("7.0"))
        self.assertEqual(change, Decimal("-3.0"))

    def test_calculate_new_stock_adjusted(self):
        new_stock, change = calculate_new_stock(
            self.ingredient,
            StockUpdate.UpdateType.ADJUSTED,
            Decimal("8.0")
        )
        self.assertEqual(new_stock, Decimal("8.0"))
        self.assertEqual(change, Decimal("-2.0"))

    def test_update_ingredient_stock_success(self):
        success, new_stock, error = update_ingredient_stock(
            self.ingredient,
            StockUpdate.UpdateType.ADDED,
            Decimal("5.0"),
            created_by=self.chef
        )

        self.assertTrue(success)
        self.assertEqual(new_stock, Decimal("15.0"))
        self.assertIsNone(error)

        # Verify database
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.current_stock, Decimal("15.0"))

        # Verify audit record
        self.assertEqual(StockUpdate.objects.count(), 1)
        update = StockUpdate.objects.first()
        self.assertEqual(update.quantity_change, Decimal("5.0"))

    def test_update_ingredient_stock_negative_check(self):
        # Try to use more than available
        success, new_stock, error = update_ingredient_stock(
            self.ingredient,
            StockUpdate.UpdateType.USED,
            Decimal("15.0"),  # More than current 10.0
            created_by=self.chef
        )

        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("negative", error.lower())

    def test_get_low_stock_ingredients(self):
        # Create low stock ingredient
        Ingredient.objects.create(
            name="Tomatoes",
            unit="each",
            current_stock=Decimal("2.0"),
            minimum_stock=Decimal("5.0"),
            category="produce"
        )

        low_stock = get_low_stock_ingredients()
        self.assertEqual(low_stock.count(), 1)
        self.assertEqual(low_stock.first().name, "Tomatoes")


class ShoppingListGenerationTests(TestCase):
    def setUp(self):
        self.chef = User.objects.create_user(
            username="chef",
            password="pass",
            role=User.Role.CHEF
        )

        # Create ingredients
        self.chicken = Ingredient.objects.create(
            name="Chicken",
            unit="lb",
            current_stock=Decimal("2.0"),
            minimum_stock=Decimal("5.0"),
            category="meat"
        )
        self.rice = Ingredient.objects.create(
            name="Rice",
            unit="cup",
            current_stock=Decimal("10.0"),
            minimum_stock=Decimal("3.0"),
            category="pantry"
        )

        # Create meal plan
        self.meal_plan = MealPlan.objects.create(
            name="Chicken Dinner",
            servings=4,
            is_active=True
        )

        # Link ingredients
        MealIngredient.objects.create(
            meal_plan=self.meal_plan,
            ingredient=self.chicken,
            quantity=Decimal("3.0"),
            unit="lb"
        )
        MealIngredient.objects.create(
            meal_plan=self.meal_plan,
            ingredient=self.rice,
            quantity=Decimal("2.0"),
            unit="cup"
        )

        # Schedule meal for tomorrow
        ActiveMealSchedule.objects.create(
            meal_plan=self.meal_plan,
            scheduled_date=timezone.now().date() + timedelta(days=1)
        )

    def test_generate_shopping_list_creates_items(self):
        items_created, items_updated, errors = generate_shopping_list_items()

        self.assertEqual(len(errors), 0)
        self.assertGreater(items_created, 0)

        # Check shopping list
        shopping_items = ShoppingListItem.objects.filter(is_manual=False)
        self.assertGreater(shopping_items.count(), 0)

        # Chicken should be in list (need 3 + min 5 - have 2 = 6)
        chicken_items = ShoppingListItem.objects.filter(ingredient=self.chicken)
        self.assertEqual(chicken_items.count(), 1)
        self.assertEqual(chicken_items.first().quantity_needed, Decimal("6.0"))


class ScheduleMealTests(TestCase):
    def setUp(self):
        self.meal_plan = MealPlan.objects.create(
            name="Test Meal",
            servings=4
        )

    def test_schedule_meal_success(self):
        today = timezone.now().date()
        success, schedule, error = schedule_meal(self.meal_plan, today)

        self.assertTrue(success)
        self.assertIsNotNone(schedule)
        self.assertIsNone(error)
        self.assertEqual(schedule.scheduled_date, today)

    def test_schedule_meal_duplicate_updates(self):
        today = timezone.now().date()

        # Schedule twice
        success1, schedule1, _ = schedule_meal(self.meal_plan, today)
        success2, schedule2, _ = schedule_meal(self.meal_plan, today)

        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertEqual(schedule1.pk, schedule2.pk)  # Same record updated
        self.assertEqual(ActiveMealSchedule.objects.count(), 1)
