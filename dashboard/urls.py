from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('teacher/', views.teacher_dashboard, name='teacher'),
    path('student/', views.student_dashboard, name='student'),
    path('parent/', views.parent_dashboard, name='parent'),
    path('create-material/', views.create_material, name='create_material'),
    path('create-assignment/', views.create_assignment, name='create_assignment'),
    path('students/', views.students_list, name='students_list'),
    path('announcement/', views.send_announcement, name='send_announcement'),
]