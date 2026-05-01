"""
Business logic layer for Kitchen Manager.
Separates business logic from views for better testability and maintainability.
"""
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from .models import (
    User, Ingredient, MealPlan, MealIngredient,
    ShoppingListItem, StockUpdate, ActiveMealSchedule
)

logger = logging.getLogger(__name__)


# --- Stock Management ---

def calculate_new_stock(ingredient, update_type, quantity_change):
    """
    Calculate new stock level based on update type.

    Args:
        ingredient: Ingredient instance
        update_type: StockUpdate.UpdateType choice
        quantity_change: Decimal quantity

    Returns:
        tuple: (new_stock, actual_change)
    """
    current = float(ingredient.current_stock)
    qty = float(quantity_change)

    if update_type == StockUpdate.UpdateType.ADJUSTED:
        # For adjusted, quantity_change IS the new stock level
        new_stock = qty
        actual_change = new_stock - current
    elif update_type == StockUpdate.UpdateType.USED:
        # Used decreases stock
        new_stock = current - qty
        actual_change = -qty
    else:  # ADDED
        # Added increases stock
        new_stock = current + qty
        actual_change = qty

    return Decimal(str(new_stock)), Decimal(str(actual_change))


@transaction.atomic
def update_ingredient_stock(
    ingredient,
    update_type,
    quantity_change,
    meal_plan=None,
    notes=None,
    created_by=None
):
    """
    Update ingredient stock and create audit record.

    Args:
        ingredient: Ingredient instance
        update_type: StockUpdate.UpdateType choice
        quantity_change: Decimal quantity
        meal_plan: Optional MealPlan instance
        notes: Optional string notes
        created_by: Optional User instance

    Returns:
        tuple: (success: bool, new_stock: Decimal, error_message: str or None)
    """
    try:
        # Validate inputs
        if quantity_change <= 0:
            raise ValidationError("Quantity change must be positive")

        # Calculate new stock
        new_stock, actual_change = calculate_new_stock(
            ingredient, update_type, quantity_change
        )

        # Ensure stock doesn't go negative
        if new_stock < 0:
            raise ValidationError("Stock cannot be negative")

        # Create update record
        update = StockUpdate(
            ingredient=ingredient,
            update_type=update_type,
            quantity_change=actual_change,
            previous_stock=ingredient.current_stock,
            new_stock=new_stock,
            meal_plan=meal_plan,
            notes=notes,
            created_by=created_by
        )
        update.full_clean()  # Run model validation
        update.save()

        # Update ingredient
        ingredient.current_stock = new_stock
        ingredient.full_clean()
        ingredient.save()

        logger.info(
            f"Stock updated for {ingredient.name} by {created_by.username if created_by else 'system'}: "
            f"{actual_change} ({update_type})"
        )

        return True, new_stock, None

    except ValidationError as e:
        logger.error(f"Validation error updating stock for {ingredient.name}: {str(e)}")
        return False, ingredient.current_stock, str(e)
    except Exception as e:
        logger.error(f"Unexpected error updating stock for {ingredient.name}: {str(e)}")
        return False, ingredient.current_stock, f"Internal error: {str(e)}"


# --- Shopping List Generation ---

def generate_shopping_list_items(scheduled_meals=None):
    """
    Generate shopping list items based on scheduled meals and low stock.

    Args:
        scheduled_meals: QuerySet of ActiveMealSchedule (optional, defaults to future meals)

    Returns:
        tuple: (items_created: int, items_updated: int, errors: list)
    """
    errors = []
    items_created = 0
    items_updated = 0

    try:
        # Get scheduled meals if not provided
        if scheduled_meals is None:
            scheduled_meals = ActiveMealSchedule.objects.filter(
                scheduled_date__gte=timezone.now().date()
            )

        # Calculate ingredient needs from meals
        ingredient_needs = {}

        for schedule in scheduled_meals:
            for meal_ing in schedule.meal_plan.ingredients.select_related('ingredient').all():
                key = (meal_ing.ingredient.id, meal_ing.unit)
                if key not in ingredient_needs:
                    ingredient_needs[key] = {
                        'ingredient': meal_ing.ingredient,
                        'quantity': Decimal('0'),
                        'unit': meal_ing.unit
                    }
                ingredient_needs[key]['quantity'] += meal_ing.quantity

        # Process each needed ingredient
        for key, data in ingredient_needs.items():
            ingredient = data['ingredient']
            needed = data['quantity']
            available = float(ingredient.current_stock)
            min_stock = float(ingredient.minimum_stock)

            # Calculate shortage
            shortage = needed + min_stock - available
            if shortage > 0:
                # Find or create shopping item
                existing = ShoppingListItem.objects.filter(
                    ingredient=ingredient,
                    is_manual=False,
                    status=ShoppingListItem.Status.PENDING
                ).first()

                if existing:
                    existing.quantity_needed = shortage
                    existing.save()
                    items_updated += 1
                else:
                    ShoppingListItem.objects.create(
                        name=ingredient.name,
                        quantity_needed=shortage,
                        unit=data['unit'],
                        is_manual=False,
                        ingredient=ingredient,
                        status=ShoppingListItem.Status.PENDING
                    )
                    items_created += 1

        # Also add items below minimum stock (not from meals)
        low_stock = Ingredient.objects.filter(current_stock__lte=F('minimum_stock'))
        for ingredient in low_stock:
            # Skip if already handled above
            if (ingredient.id, ingredient.unit) in ingredient_needs:
                continue

            shortage = float(ingredient.minimum_stock) - float(ingredient.current_stock)
            existing = ShoppingListItem.objects.filter(
                ingredient=ingredient,
                is_manual=False,
                status=ShoppingListItem.Status.PENDING
            ).first()

            if not existing:
                ShoppingListItem.objects.create(
                    name=ingredient.name,
                    quantity_needed=shortage,
                    unit=ingredient.unit,
                    is_manual=False,
                    ingredient=ingredient,
                    status=ShoppingListItem.Status.PENDING
                )
                items_created += 1

        logger.info(f"Shopping list generated: {items_created} created, {items_updated} updated")
        return items_created, items_updated, errors

    except Exception as e:
        logger.error(f"Error generating shopping list: {str(e)}")
        errors.append(str(e))
        return 0, 0, errors


# --- Ingredient Management ---

def get_low_stock_ingredients():
    """Get all ingredients below minimum stock level."""
    return Ingredient.objects.filter(current_stock__lte=F('minimum_stock')).order_by('category', 'name')


def get_ingredients_by_category(category=None):
    """Get ingredients filtered by category."""
    if category:
        return Ingredient.objects.filter(category=category).order_by('name')
    return Ingredient.objects.all().order_by('category', 'name')


# --- Meal Planning ---

def get_upcoming_meals(days=7):
    """Get meal schedules for the next N days."""
    from datetime import timedelta
    end_date = timezone.now().date() + timedelta(days=days)
    return ActiveMealSchedule.objects.filter(
        scheduled_date__gte=timezone.now().date(),
        scheduled_date__lte=end_date
    ).select_related('meal_plan').order_by('scheduled_date')


def schedule_meal(meal_plan, scheduled_date, confirmed=False):
    """
    Schedule a meal for a specific date.

    Returns:
        tuple: (success: bool, schedule: ActiveMealSchedule or None, error: str or None)
    """
    try:
        schedule, created = ActiveMealSchedule.objects.get_or_create(
            meal_plan=meal_plan,
            scheduled_date=scheduled_date,
            defaults={'is_confirmed': confirmed}
        )

        if not created:
            schedule.is_confirmed = confirmed
            schedule.save()
            logger.info(f"Updated meal schedule: {meal_plan.name} on {scheduled_date}")
        else:
            logger.info(f"Scheduled meal: {meal_plan.name} on {scheduled_date}")

        return True, schedule, None

    except Exception as e:
        logger.error(f"Error scheduling meal: {str(e)}")
        return False, None, str(e)
