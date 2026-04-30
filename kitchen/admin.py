from django.contrib import admin
from .models import User, Ingredient, MealPlan, MealIngredient, ShoppingListItem, StockUpdate, ActiveMealSchedule

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_stock', 'unit', 'minimum_stock', 'category', 'needs_reorder']
    list_filter = ['category']
    search_fields = ['name']
    list_editable = ['current_stock', 'minimum_stock']

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'servings', 'prep_time_minutes', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(MealIngredient)
class MealIngredientAdmin(admin.ModelAdmin):
    list_display = ['meal_plan', 'ingredient', 'quantity', 'unit']
    list_filter = ['meal_plan']

@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity_needed', 'unit', 'status', 'is_manual', 'created_at']
    list_filter = ['status', 'is_manual']
    search_fields = ['name']

@admin.register(StockUpdate)
class StockUpdateAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'update_type', 'quantity_change', 'new_stock', 'created_at']
    list_filter = ['update_type', 'created_at']
    search_fields = ['ingredient__name']

@admin.register(ActiveMealSchedule)
class ActiveMealScheduleAdmin(admin.ModelAdmin):
    list_display = ['meal_plan', 'scheduled_date', 'is_confirmed']
    list_filter = ['is_confirmed', 'scheduled_date']
