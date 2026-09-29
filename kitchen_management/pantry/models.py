from django.db import models

class PantryItem(models.Model):
    # Fields that make up a model
    name = models.CharField(max_length=256)  # Text field for item name
    category = models.CharField(max_length=100)  # e.g., 'Grains', 'Oil'
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # Quantity (float)
    unit = models.CharField(max_length=50)  # e.g., 'kg', 'L', 'pieces'
    added_date = models.DateTimeField(auto_now_add=True)  # When it was added
    
    def __str__(self):
        return f"{self.name} - {self.quantity} {self.unit}"

class PantryImage(models.Model):
    # An optional link to an image (or a reference to a stored file)
    item = models.ForeignKey(PantryItem, on_delete=models.CASCADE, related_name='images')
    file = models.FileField(upload_to='pantry_images/')  # Store file paths
    
    def __str__(self):
        return f"Image for {self.item.name}"
