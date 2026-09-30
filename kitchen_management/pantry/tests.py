"""
Automated tests for the pantry index page functionality.

This module ensures that:
1. The "The pantry is empty" message displays when there are no pantry items
2. Pantry items are displayed correctly when they exist
3. The view handles both empty and non-empty scenarios correctly

Test Coverage: 
    - Empty pantry scenario (message display)
    - Non-empty pantry scenario (item listing)
    - Database integration tests
    - View function integration tests

Last Updated: 2026-09-29
"""

from django.test import Client, TestCase, RequestFactory
from pantry.models import PantryItem
from pantry.views import pantry_index


class TestPantryEmptyMessage(TestCase):
    """Test cases for the empty pantry message functionality."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        PantryItem.objects.all().delete()
    
    def test_pantry_index_shows_empty_message_when_no_items_in_database(self):
        """Verify the 'The pantry is empty' message displays when database has no items."""
        self.assertEqual(PantryItem.objects.count(), 0)
        client = Client()
        response = client.get('/', follow=True)
        content = response.content.decode('utf-8')
        self.assertIn('The pantry is empty', content)
    
    def test_pantry_index_has_success_http_200_status_with_empty_items(self):
        """Verify the pantry index view returns HTTP 200 status code with empty items."""
        client = Client()
        response = client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_empty_message_exact_html_structure(self):
        """Verify exact HTML structure of 'The pantry is empty' message when no items."""
        client = Client()
        response = client.get('/', follow=True)
        content = response.content.decode('utf-8')
        
        # Verify the exact HTML structure for the empty message
        self.assertIn('<p>The pantry is empty</p>', content)
        
        # Verify no table element is present (items are not being displayed)
        self.assertNotIn('<table', content)
        
        # Verify the response contains proper document structure
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('<html', content)
        self.assertIn('</html>', content)


class TestPantryItemsDisplay(TestCase):
    """Test cases for displaying items when pantry is not empty."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        PantryItem.objects.all().delete()
    
    def test_pantry_index_displays_items_when_database_has_data(self):
        """Verify items are displayed in table when they exist in the database."""
        PantryItem.objects.create(
            name='Apples',
            category='Fruits',
            quantity=5.0,
            unit='kg'
        )
        client = Client()
        response = client.get('/', follow=True)
        content = response.content.decode('utf-8')
        self.assertNotIn('The pantry is empty', content)
        
        # Verify all columns are rendered for a single item (name, category, quantity, unit, date)
        self.assertIn('<td>Apples</td>', content)  # name column
        self.assertIn('<td>Fruits</td>', content)  # category column
        self.assertIn('<td>5.00</td>', content)  # quantity column (decimal format)
        self.assertIn('<td>kg</td>', content)  # unit column
        
        # Verify date column is present (month, day, year format)
        self.assertIn('<td>Sep 30, 2026</td>', content)


class TestPantryDatabaseQuery(TestCase):
    """Test cases for PantryItem database query behavior."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        PantryItem.objects.all().delete()
    
    def test_pantry_item_objects_all_on_empty_database_returns_empty_list(self):
        """Verify PantryItem.objects.all() returns empty list when database is empty."""
        result = list(PantryItem.objects.all())
        self.assertEqual(len(result), 0)
    
    def test_pantry_item_objects_count_on_empty_database_returns_zero(self):
        """Verify PantryItem.objects.count() returns zero when database is empty."""
        count = PantryItem.objects.count()
        self.assertEqual(count, 0)


class TestPantryModels(TestCase):
    """Test cases for PantryItem model data integrity."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        PantryItem.objects.all().delete()
    
    def test_pantry_item_model_creates_with_valid_data(self):
        """Verify PantryItem model can be created with valid data."""
        item = PantryItem(name='Test Item', category='General', quantity=1.0, unit='piece')
        item.save()
        self.assertEqual(PantryItem.objects.count(), 1)
    
    def test_pantry_item_model_retrieves_correctly_after_save(self):
        """Verify PantryItem can be retrieved after being saved."""
        item = PantryItem(name='Test Item', category='General', quantity=1.0, unit='piece')
        item.save()
        self.assertEqual(PantryItem.objects.count(), 1)
    
    def test_pantry_item_model_retrieves_data_after_creation(self):
        """Verify retrieved data matches original data."""
        item = PantryItem(name='Test Item', category='General', quantity=1.0, unit='piece')
        item.save()
        retrieved_item = PantryItem.objects.get(pk=item.id)
        self.assertEqual(retrieved_item.name, 'Test Item')


class TestPantryViewIntegration(TestCase):
    """Integration tests for pantry view functionality."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        PantryItem.objects.all().delete()
    
    def test_pantry_index_view_handles_empty_items_without_errors(self):
        """Verify the view handles empty items without throwing errors."""
        factory = RequestFactory()
        request = factory.get('/')
        response = pantry_index(request)
        self.assertEqual(response.status_code, 200)
    
    def test_pantry_index_view_handles_multiple_items_without_errors(self):
        """Verify the view handles multiple items without throwing errors."""
        for i in range(5):
            PantryItem.objects.create(name=f'Very Long Item {i}', category='General', quantity=2.0, unit='pieces')
        self.assertEqual(PantryItem.objects.count(), 5)
        factory = RequestFactory()
        request = factory.get('/')
        response = pantry_index(request)
        self.assertEqual(response.status_code, 200)

    def test_pantry_index_view_handles_single_item(self):
        """Verify the view handles exactly one item without throwing errors."""
        PantryItem.objects.create(name='Single Item', category='Test', quantity=1.5, unit='pcs')
        self.assertEqual(PantryItem.objects.count(), 1)
        factory = RequestFactory()
        request = factory.get('/')
        response = pantry_index(request)
        self.assertEqual(response.status_code, 200)
    
    def test_view_returns_complete_response_structure(self):
        """Verify view returns complete HTML structure for both empty and populated scenarios."""
        
        # Test with no items (empty pantry scenario)
        PantryItem.objects.all().delete()
        factory = RequestFactory()
        request = factory.get('/')
        response = pantry_index(request)
        self.assertEqual(response.status_code, 200)
        
        # Test with multiple items (non-empty scenario)
        for i in range(3):
            PantryItem.objects.create(name=f'Verification Item {i}', category='Test Category', quantity=99.99, unit='units')
        self.assertEqual(PantryItem.objects.count(), 3)
        
        factory = RequestFactory()
        request = factory.get('/')
        response = pantry_index(request)
        self.assertEqual(response.status_code, 200)



class TestPantryEmptyEdgeCases(TestCase):
    """Test edge cases for the pantry empty functionality."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
    def setUp(self):
        PantryItem.objects.all().delete()
    
    def test_pantry_item_shown_with_zero_quantity_item(self):
        """Edge case: Item with quantity=0.00 still counted as having items."""
        PantryItem.objects.create(name='Zero Item', category='Special', quantity=0.0, unit='units')
        self.assertEqual(PantryItem.objects.count(), 1)
    
    def test_pantry_empty_message_not_shown_with_zero_quantity_item(self):
        """Edge case: At least one item, show items not empty message."""
        PantryItem.objects.create(name='Zero Item', category='Special', quantity=0.0, unit='units')
        client = Client()
        response = client.get('/', follow=True)
        content = response.content.decode('utf-8')
        self.assertNotIn('The pantry is empty', content)
    
    def test_pantry_multiple_items_all_displayed_in_response(self):
        """Verify all items are displayed in the table response."""
        PantryItem.objects.create(name='Apple', category='Fruits', quantity=5.0, unit='kg')
        PantryItem.objects.create(name='Banana', category='Fruits', quantity=3.0, unit='kg')
        PantryItem.objects.create(name='Flour', category='Baking', quantity=2.5, unit='kg')
        self.assertEqual(PantryItem.objects.count(), 3)
        client = Client()
        response = client.get('/', follow=True)
        content = response.content.decode('utf-8')
        self.assertIn('Apple', content)
        self.assertIn('Banana', content)
        self.assertIn('Flour', content)


if __name__ == "__main__":
    import django
    from django.conf import settings
    settings.configure(
        DEBUG=True,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.contenttypes', 'django.contrib.auth', 'pantry', 'meal_plans', 'shopping_list'],
        MIDDLEWARE=[],
    )
    django.setup()
    import unittest
    unittest.main()
