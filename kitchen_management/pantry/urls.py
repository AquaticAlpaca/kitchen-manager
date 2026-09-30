from django.urls import path
from . import views

urlpatterns = [
    path('', views.pantry_index, name='pantry-index'),
]
