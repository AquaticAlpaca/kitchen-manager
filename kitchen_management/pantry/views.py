from django.shortcuts import render
from pantry.models import PantryItem

def pantry_index(request):
    """View function to display the pantry index page."""
    items = PantryItem.objects.all()
    return render(request, 'pantry/index.html', {'items': items})
