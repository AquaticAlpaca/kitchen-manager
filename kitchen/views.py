from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import F
from django.utils import timezone
from .models import User, Ingredient, MealPlan, ShoppingListItem, ActiveMealSchedule, StockUpdate
from .forms import (
    ChefRegistrationForm, BuyerRegistrationForm, IngredientForm,
    MealPlanForm, MealIngredientForm, StockUpdateForm,
    ShoppingListItemForm, ActiveMealScheduleForm
)


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
    active_meals = ActiveMealSchedule.objects.filter(scheduled_date__gte=timezone.now().date())[:5]

    context = {
        'low_stock_count': Ingredient.objects.filter(current_stock__lte=F('minimum_stock')).count(),
        'active_meals': active_meals,
        'total_ingredients': Ingredient.objects.count(),
    }
    return render(request, 'kitchen/chef_dashboard.html', context)


@login_required
@user_passes_test(is_buyer)
def buyer_dashboard(request):
    """Buyer-specific dashboard"""
    pending_items = ShoppingListItem.objects.filter(status=ShoppingListItem.Status.PENDING)
    upcoming_meals = ActiveMealSchedule.objects.filter(scheduled_date__gte=timezone.now().date())[:5]

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
            update = form.save(commit=False)
            update.ingredient = ingredient
            update.previous_stock = ingredient.current_stock

            # Handle different update types
            if update.update_type == StockUpdate.UpdateType.ADJUSTED:
                # For adjusted, quantity_change IS the new stock level
                update.new_stock = update.quantity_change
                update.quantity_change = update.new_stock - update.previous_stock
            elif update.update_type == StockUpdate.UpdateType.USED:
                # For used/added, quantity_change is the delta
                update.new_stock = ingredient.current_stock - update.quantity_change
            else:  # ADDED
                update.new_stock = ingredient.current_stock + update.quantity_change

            update.created_by = request.user

            # Save the update record
            update.save()

            # Update the ingredient stock
            ingredient.current_stock = update.new_stock
            ingredient.save()

            messages.success(request, f'Stock updated! New amount: {update.new_stock} {ingredient.unit}')
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
@user_passes_test(is_chef)
def generate_shopping_list(request):
    """Generate shopping list based on meal plans and low stock"""
    if request.method == 'POST':
        # Get all scheduled meals
        scheduled_meals = ActiveMealSchedule.objects.filter(scheduled_date__gte=timezone.now().date())

        # Calculate needed ingredients
        ingredient_needs = {}

        for schedule in scheduled_meals:
            for meal_ing in schedule.meal_plan.ingredients.all():
                key = (meal_ing.ingredient.id, meal_ing.unit)
                if key not in ingredient_needs:
                    ingredient_needs[key] = {
                        'ingredient': meal_ing.ingredient,
                        'quantity': 0,
                        'unit': meal_ing.unit
                    }
                ingredient_needs[key]['quantity'] += float(meal_ing.quantity)

        # Check against current stock and minimum
        for key, data in ingredient_needs.items():
            ingredient = data['ingredient']
            needed = data['quantity']
            available = float(ingredient.current_stock)
            min_stock = float(ingredient.minimum_stock)

            # Calculate shortage
            shortage = needed + min_stock - available
            if shortage > 0:
                # Create or update shopping item
                existing = ShoppingListItem.objects.filter(
                    ingredient=ingredient,
                    is_manual=False,
                    status=ShoppingListItem.Status.PENDING
                ).first()

                if existing:
                    existing.quantity_needed = shortage
                    existing.save()
                else:
                    ShoppingListItem.objects.create(
                        name=ingredient.name,
                        quantity_needed=shortage,
                        unit=data['unit'],
                        is_manual=False,
                        ingredient=ingredient,
                        status=ShoppingListItem.Status.PENDING
                    )

        # Also add items below minimum stock (not from meals)
        low_stock = Ingredient.objects.filter(current_stock__lte=F('minimum_stock'))
        for ingredient in low_stock:
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

        messages.success(request, 'Shopping list generated based on meal plans!')
        return redirect('kitchen:shopping_list')

    return render(request, 'kitchen/generate_shopping.html')


@login_required
@user_passes_test(is_chef)
def meal_plan_list(request):
    """List all meal plans"""
    meal_plans = MealPlan.objects.all()
    return render(request, 'kitchen/meal_plans/list.html', {'meal_plans': meal_plans})


@login_required
@user_passes_test(is_chef)
def meal_plan_create(request):
    """Create new meal plan"""
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            meal_plan = form.save()
            messages.success(request, 'Meal plan created!')
            return redirect('kitchen:meal_plan_ingredients', pk=meal_plan.pk)
    else:
        form = MealPlanForm()
    return render(request, 'kitchen/meal_plans/form.html', {'form': form, 'title': 'Add Meal Plan'})


@login_required
@user_passes_test(is_chef)
def meal_plan_ingredients(request, pk):
    """Manage ingredients for a meal plan"""
    meal_plan = get_object_or_404(MealPlan, pk=pk)
    meal_ingredients = meal_plan.ingredients.all()

    if request.method == 'POST':
        form = MealIngredientForm(request.POST)
        if form.is_valid():
            meal_ing = form.save(commit=False)
            meal_ing.meal_plan = meal_plan
            meal_ing.save()
            messages.success(request, 'Ingredient added to meal plan!')
            return redirect('kitchen:meal_plan_ingredients', pk=pk)
    else:
        form = MealIngredientForm()

    return render(request, 'kitchen/meal_plans/ingredients.html', {
        'meal_plan': meal_plan,
        'meal_ingredients': meal_ingredients,
        'form': form
    })

@login_required
@user_passes_test(is_chef)
def delete_meal_ingredient(request, pk):
    """Remove an ingredient from a meal plan"""
    meal_ingredient = get_object_or_404(MealIngredient, pk=pk)
    meal_plan = meal_ingredient.meal_plan

    if request.method == 'POST':
        ingredient_name = meal_ingredient.ingredient.name
        meal_ingredient.delete()
        messages.success(request, f'{ingredient_name} removed from {meal_plan.name}.')

    return redirect('kitchen:meal_plan_ingredients', pk=meal_plan.pk)

@login_required
@user_passes_test(is_chef)
def schedule_meal(request):
    """Schedule a meal for a specific date"""
    if request.method == 'POST':
        form = ActiveMealScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save()
            messages.success(request, f'{schedule.meal_plan.name} scheduled for {schedule.scheduled_date}!')
            return redirect('kitchen:dashboard')
    else:
        form = ActiveMealScheduleForm()

    return render(request, 'kitchen/schedule_meal.html', {'form': form})
