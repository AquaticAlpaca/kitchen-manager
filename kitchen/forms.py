from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Ingredient, MealPlan, MealIngredient, ShoppingListItem, StockUpdate, ActiveMealSchedule

class ChefRegistrationForm(UserCreationForm):
    """Form for chef registration"""

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = User.Role.CHEF
        self.fields['role'].widget = forms.HiddenInput()


class BuyerRegistrationForm(UserCreationForm):
    """Form for buyer registration"""

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].initial = User.Role.BUYER
        self.fields['role'].widget = forms.HiddenInput()


class IngredientForm(forms.ModelForm):
    """Form for ingredient management"""

    class Meta:
        model = Ingredient
        fields = ['name', 'unit', 'current_stock', 'minimum_stock', 'category', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ingredient name'}),
            'unit': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'minimum_stock': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MealPlanForm(forms.ModelForm):
    """Form for meal plan management"""

    class Meta:
        model = MealPlan
        fields = ['name', 'description', 'servings', 'prep_time_minutes', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'servings': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'prep_time_minutes': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MealIngredientForm(forms.ModelForm):
    """Form for linking ingredients to meals"""

    class Meta:
        model = MealIngredient
        fields = ['ingredient', 'quantity', 'unit']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., cups, lbs'}),
        }


class StockUpdateForm(forms.ModelForm):
    """Form for updating ingredient stock"""

    class Meta:
        model = StockUpdate
        fields = ['update_type', 'quantity_change', 'meal_plan', 'notes']
        widgets = {
            'update_type': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'quantity_change': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'meal_plan': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ShoppingListItemForm(forms.ModelForm):
    """Form for shopping list items"""

    class Meta:
        model = ShoppingListItem
        fields = ['name', 'quantity_needed', 'unit', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Item name'}),
            'quantity_needed': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., cups, lbs'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ActiveMealScheduleForm(forms.ModelForm):
    """Form for scheduling meals"""

    class Meta:
        model = ActiveMealSchedule
        fields = ['meal_plan', 'scheduled_date']
        widgets = {
            'meal_plan': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control form-control-lg',
                'type': 'date'
            }),
        }
