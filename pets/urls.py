from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.home, name="home"),
    path("pets/", views.pet_list, name="pet_list"),
    path("pets/<int:pk>/", views.pet_detail, name="pet_detail"),
    path("pets/<int:pk>/adopt/", views.adopt, name="adopt"),
    path("my-requests/", views.my_requests, name="my_requests"),
    path("profile/", views.profile, name="profile"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(authentication_form=LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
