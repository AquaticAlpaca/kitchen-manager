from django.urls import path
from . import views

app_name = 'kitchen'

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Ingredients (Chef only)
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/new/', views.ingredient_create, name='ingredient_create'),
    path('ingredients/<int:pk>/edit/', views.ingredient_update, name='ingredient_update'),
    path('ingredients/<int:pk>/stock/', views.stock_update, name='stock_update'),

    # Meal Plans (Chef only)
    path('meal-plans/', views.meal_plan_list, name='meal_plan_list'),
    path('meal-plans/new/', views.meal_plan_create, name='meal_plan_create'),
    path('meal-plans/<int:pk>/ingredients/', views.meal_plan_ingredients, name='meal_plan_ingredients'),

    # Shopping List (Buyer only)
    path('shopping-list/', views.shopping_list, name='shopping_list'),
    path('shopping-list/add/', views.shopping_item_create, name='shopping_item_create'),
    path('shopping-list/<int:pk>/status/', views.shopping_item_update_status, name='shopping_item_update_status'),
    path('shopping-list/<int:pk>/delete/', views.shopping_item_delete, name='shopping_item_delete'),

    # Generate Shopping List (Chef)
    path('generate-shopping/', views.generate_shopping_list, name='generate_shopping_list'),

    # Schedule Meals (Chef)
    path('schedule-meal/', views.schedule_meal, name='schedule_meal'),
]
