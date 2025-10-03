from django.urls import path
from . import views

app_name = 'hub'

urlpatterns = [
    path('', views.materials_list, name='materials_list'),
    path('material/<int:pk>/', views.material_detail, name='material_detail'),
    path('assignments/', views.assignments_list, name='assignments_list'),
    path('progress/', views.progress_view, name='progress'),
]