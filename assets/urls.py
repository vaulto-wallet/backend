from django.conf.urls import url, re_path
from . import views

urlpatterns = [
    url(r'assets/', views.AssetView.as_view(), name='assets'),
]