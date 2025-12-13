from django.urls import path, include

urlpatterns = [
    path('auth/', include('apps.accounts.urls')),
    path('enrollees/', include('apps.enrollees.urls')),
]