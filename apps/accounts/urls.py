from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('refresh', views.refresh, name='refresh'),
    path('profile', views.profile_view, name="profile"),
    path('employer/dashboard/', views.employer_dashboard, name='employer-dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee-dashboard'),
]