from django.urls import path
from . import views


urlpatterns = [
    path('', views.enrollees_list_create, name='enrollee-list-create'),
    path('bulk-upload/', views.bulk_upload_enrollee, name='bulk-upload'),
    path('<str:enrollee_id>/', views.enrollee_detail, name='enrollee-detail'),
]