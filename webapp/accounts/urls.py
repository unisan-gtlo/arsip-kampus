from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.AccountsLoginView.as_view(), name="login"),
    path("logout/", views.AccountsLogoutView.as_view(), name="logout"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/add/", views.UserCreateView.as_view(), name="user_add"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user_delete"),
]
