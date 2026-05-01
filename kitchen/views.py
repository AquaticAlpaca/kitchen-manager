# Top of file - add imports
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import User, Ingredient, MealPlan, MealIngredient, ShoppingListItem, StockUpdate, ActiveMealSchedule
from .forms import (
    ChefRegistrationForm, BuyerRegistrationForm, IngredientForm,
    MealPlanForm, MealIngredientForm, StockUpdateForm,
    ShoppingListItemForm, ActiveMealScheduleForm
)
from .services import (
    update_ingredient_stock,
    generate_shopping_list_items,
    get_low_stock_ingredients,
    get_upcoming_meals,
    schedule_meal
)

logger = logging.getLogger(__name__)

# ... keep existing helper functions (is_chef, is_buyer) ...

# Update stock_update view
@login_required
@user_passes_test(is_chef)
def stock_update(request, pk):
    """Update ingredient stock"""
    ingredient = get_object_or_404(Ingredient, pk=pk)

    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            success, new_stock, error = update_ingredient_stock(
                ingredient=ingredient,
                update_type=form.cleaned_data['update_type'],
                quantity_change=form.cleaned_data['quantity_change'],
                meal_plan=form.cleaned_data.get('meal_plan'),
                notes=form.cleaned_data.get('notes'),
                created_by=request.user
            )

            if success:
                messages.success(request, f'Stock updated! New amount: {new_stock} {ingredient.unit}')
            else:
                messages.error(request, f"Failed to update stock: {error}")

            return redirect('kitchen:ingredient_list')
    else:
        form = StockUpdateForm()

    return render(request, 'kitchen/stock_update.html', {
        'form': form,
        'ingredient': ingredient,
        'current_stock': ingredient.current_stock
    })

# Update generate_shopping_list view
@login_required
@user_passes_test(is_chef)
def generate_shopping_list(request):
    """Generate shopping list based on meal plans and low stock"""
    if request.method == 'POST':
        scheduled_meals = ActiveMealSchedule.objects.filter(
            scheduled_date__gte=timezone.now().date()
        )

        items_created, items_updated, errors = generate_shopping_list_items(scheduled_meals)

        if errors:
            messages.error(request, f"Error generating shopping list: {errors[0]}")
        else:
            total = items_created + items_updated
            messages.success(request, f'Shopping list updated! {items_created} new items, {items_updated} updated.')

        return redirect('kitchen:shopping_list')

    return render(request, 'kitchen/generate_shopping.html')

# Update chef_dashboard view
@login_required
@user_passes_test(is_chef)
def chef_dashboard(request):
    """Chef-specific dashboard"""
    low_stock = get_low_stock_ingredients()
    active_meals = get_upcoming_meals(days=7)[:5]

    context = {
        'low_stock_count': low_stock.count(),
        'active_meals': active_meals,
        'total_ingredients': Ingredient.objects.count(),
        'low_stock_items': low_stock[:5]  # Show first 5 low stock items
    }
    return render(request, 'kitchen/chef_dashboard.html', context)

# Update buyer_dashboard view
@login_required
@user_passes_test(is_buyer)
def buyer_dashboard(request):
    """Buyer-specific dashboard"""
    pending_items = ShoppingListItem.objects.filter(status=ShoppingListItem.Status.PENDING)
    upcoming_meals = get_upcoming_meals(days=7)[:5]

    context = {
        'pending_items': pending_items,
        'upcoming_meals': upcoming_meals,
        'total_pending': pending_items.count(),
    }
    return render(request, 'kitchen/buyer_dashboard.html', context)

# Update schedule_meal view
@login_required
@user_passes_test(is_chef)
def schedule_meal(request):
    """Schedule a meal for a specific date"""
    if request.method == 'POST':
        form = ActiveMealScheduleForm(request.POST)
        if form.is_valid():
            meal_plan = form.cleaned_data['meal_plan']
            scheduled_date = form.cleaned_data['scheduled_date']

            success, schedule, error = schedule_meal(meal_plan, scheduled_date)

            if success:
                messages.success(request, f'{schedule.meal_plan.name} scheduled for {schedule.scheduled_date}!')
            else:
                messages.error(request, f"Failed to schedule meal: {error}")

            return redirect('kitchen:dashboard')
    else:
        form = ActiveMealScheduleForm()

    return render(request, 'kitchen/schedule_meal.html', {'form': form})
