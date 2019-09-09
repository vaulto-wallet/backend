from django.urls import path
from . import views

urlpatterns = [
    path(r'keys/', views.KeyDetails.as_view(), name='privkey-create'),
    path(r'keys/share/', views.key_share, name='privkey-share'),
    path(r'address/<int:pk>/<int:n>/', views.key_address, name='address-get'),
    path(r'address/<int:pk>/', views.key_addresses, name='addresses-get'),
    path(r'address/validate/<str:address>/', views.address_validate, name='address-validate'),

]
