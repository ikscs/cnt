from django.urls import path
from .views import login_form, protected_view

urlpatterns = [
    path('test-login/', login_form, name='login-form'),
    path('token-check/', protected_view, name='token-check'),
    path('protected/', protected_view, name='protected'),
]
