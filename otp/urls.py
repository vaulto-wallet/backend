from django.urls import path
from . import views

urlpatterns = [
    path(r'otp/', views.OTPView.as_view(), name='otp'),
]