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

def is_chef(user):
    return user.is_authenticated and user.is_chef()


def is_buyer(user):
    return user.is_authenticated and user.is_buyer()


def register(request):
    """Registration view with role selection"""
    if request.user.is_authenticated:
        return redirect('kitchen:dashboard')

    if request.method == 'POST':
        role = request.POST.get('role')
        if role == User.Role.CHEF:
            form = ChefRegistrationForm(request.POST)
        else:
            form = BuyerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome! You are registered as a {user.get_role_display()}.')
            return redirect('kitchen:dashboard')
    else:
        form = ChefRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('kitchen:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('kitchen:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'registration/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('kitchen:login')


@login_required
def dashboard(request):
    """Main dashboard - shows different content based on role"""
    if request.user.is_chef():
        return chef_dashboard(request)
    else:
        return buyer_dashboard(request)


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


@login_required
@user_passes_test(is_chef)
def ingredient_list(request):
    """List all ingredients"""
    ingredients = Ingredient.objects.all()
    return render(request, 'kitchen/ingredients/list.html', {'ingredients': ingredients})


@login_required
@user_passes_test(is_chef)
def ingredient_create(request):
    """Create new ingredient"""
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingredient created successfully!')
            return redirect('kitchen:ingredient_list')
    else:
        form = IngredientForm()
    return render(request, 'kitchen/ingredients/form.html', {'form': form, 'title': 'Add Ingredient'})


@login_required
@user_passes_test(is_chef)
def ingredient_update(request, pk):
    """Update ingredient"""
    ingredient = get_object_or_404(Ingredient, pk=pk)
    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ingredient updated successfully!')
            return redirect('kitchen:ingredient_list')
    else:
        form = IngredientForm(instance=ingredient)
    return render(request, 'kitchen/ingredients/form.html', {'form': form, 'title': 'Edit Ingredient'})


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


@login_required
@user_passes_test(is_buyer)
def shopping_list(request):
    """View and manage shopping list"""
    items = ShoppingListItem.objects.all()
    return render(request, 'kitchen/shopping_list.html', {'items': items})


@login_required
@user_passes_test(is_buyer)
def shopping_item_create(request):
    """Add manual shopping list item"""
    if request.method == 'POST':
        form = ShoppingListItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.is_manual = True
            item.status = ShoppingListItem.Status.PENDING
            item.save()
            messages.success(request, 'Item added to shopping list!')
            return redirect('kitchen:shopping_list')
    else:
        form = ShoppingListItemForm()
    return render(request, 'kitchen/shopping_item_form.html', {'form': form})


@login_required
@user_passes_test(is_buyer)
def shopping_item_update_status(request, pk):
    """Update shopping item status"""
    item = get_object_or_404(ShoppingListItem, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(ShoppingListItem.Status.choices):
            item.status = status
            item.save()

            if status == ShoppingListItem.Status.UNAVAILABLE or status == ShoppingListItem.Status.OUT_OF_BUDGET:
                messages.warning(request, f'{item.name} marked as {item.get_status_display()}')
            else:
                messages.success(request, f'{item.name} marked as {item.get_status_display()}')

    return redirect('kitchen:shopping_list')


@login_required
@user_passes_test(is_buyer)
def shopping_item_delete(request, pk):
    """Delete shopping list item"""
    item = get_object_or_404(ShoppingListItem, pk=pk)

    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'{item_name} removed from shopping list.')

    return redirect('kitchen:shopping_list')


@login_required
@user_passes_test(is_buyer)
def bulk_delete_shopping_items(request):
    """Delete multiple selected shopping list items"""
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        deleted_count = 0

        for item_id in item_ids:
            try:
                item = ShoppingListItem.objects.get(pk=item_id)
                item.delete()
                deleted_count += 1
            except ShoppingListItem.DoesNotExist:
                continue

        messages.success(request, f'{deleted_count} item(s) deleted successfully.')
        return redirect('kitchen:shopping_list')

    return redirect('kitchen:shopping_list')


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
