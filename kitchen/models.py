from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal

class User(AbstractUser):
    """Custom user model with role-based access"""

    class Role(models.TextChoices):
        CHEF = 'chef', 'Chef'
        BUYER = 'buyer', 'Buyer'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.BUYER
    )
    phone_number = models.CharField(max_length=20, blank=True)

    # Add related_name to prevent conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='kitchen_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='kitchen_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def is_chef(self):
        return self.role == self.Role.CHEF

    def is_buyer(self):
        return self.role == self.Role.BUYER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Ingredient(models.Model):
    """Ingredient inventory tracking"""

    name = models.CharField(max_length=100)
    unit = models.CharField(
        max_length=20,
        choices=[
            ('cup', 'Cups'),
            ('tbsp', 'Tablespoons'),
            ('tsp', 'Teaspoons'),
            ('lb', 'Pounds'),
            ('oz', 'Ounces'),
            ('gallon', 'Gallons'),
            ('quart', 'Quarts'),
            ('pint', 'Pints'),
            ('each', 'Each'),
        ]
    )
    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    minimum_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('produce', 'Produce'),
            ('dairy', 'Dairy'),
            ('meat', 'Meat'),
            ('pantry', 'Pantry'),
            ('frozen', 'Frozen'),
            ('spices', 'Spices'),
            ('other', 'Other'),
        ],
        default='other'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"

    @property
    def needs_reorder(self):
        return self.current_stock <= self.minimum_stock


class MealPlan(models.Model):
    """Meal plan with ingredient requirements"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    servings = models.PositiveIntegerField(default=4)
    prep_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class MealIngredient(models.Model):
    """Link ingredients to meal plans with quantities"""

    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit = models.CharField(max_length=20)  # Store original unit for reference

    class Meta:
        unique_together = ['meal_plan', 'ingredient']

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.name} for {self.meal_plan.name}"


class ShoppingListItem(models.Model):
    """Individual item on shopping list"""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PURCHASED = 'purchased', 'Purchased'
        UNAVAILABLE = 'unavailable', 'Unavailable'
        OUT_OF_BUDGET = 'out_of_budget', 'Out of Budget'

    name = models.CharField(max_length=100)
    quantity_needed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    is_manual = models.BooleanField(
        default=False,
        help_text="True if added manually by buyer (not from meal plan)"
    )
    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shopping_items'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shopping_items'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_manual', 'status', 'name']

    def __str__(self):
        return f"{self.quantity_needed} {self.unit} {self.name}"


class StockUpdate(models.Model):
    """Track ingredient stock changes"""

    class UpdateType(models.TextChoices):
        USED = 'used', 'Used in cooking'
        ADDED = 'added', 'Added to stock'
        ADJUSTED = 'adjusted', 'Manual adjustment'

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='stock_updates'
    )
    update_type = models.CharField(
        max_length=20,
        choices=UpdateType.choices
    )
    quantity_change = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    previous_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    new_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    meal_plan = models.ForeignKey(
        MealPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ingredient.name}: {self.quantity_change} ({self.get_update_type_display()})"


class ActiveMealSchedule(models.Model):
    """Track which meals are scheduled for which days"""

    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['meal_plan', 'scheduled_date']

    def __str__(self):
        return f"{self.meal_plan.name} on {self.scheduled_date}"
