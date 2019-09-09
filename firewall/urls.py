from django.conf.urls import url, re_path
from . import views

urlpatterns = [
    url(r'firewall/', views.FirewallView.as_view(), name='firewall'),
]