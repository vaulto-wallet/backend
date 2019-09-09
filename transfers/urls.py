from django.conf.urls import url, re_path
from . import views

urlpatterns = [
    url(r'transfers/confirm/', views.transfer_confirm, name='confirmations'),
    url(r'transfers/', views.TransferRequestView.as_view(), name='transfers'),
]
