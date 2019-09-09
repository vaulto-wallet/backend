from django.conf.urls import url, re_path
from . import views

urlpatterns = [
    url(r'api/users/worker/', views.WorkerAPI.as_view(), name='account-create'),
    url(r'api/users/register/', views.UserAPI.as_view(), name='account-create'),
    url(r'api/users/groups/', views.GroupsAPI.as_view(), name='groups'),
    url(r'api/account/', views.AccountCreate.as_view(), name='key-create'),
    url(r'api/accounts/', views.accounts_list, name='accounts-list'),
    url(r'api/users/list/', views.UserList.as_view(), name='users-list'),
]