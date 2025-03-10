from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('', views.Accounts.as_view(), name='accounts'),
    path('register/', views.Register.as_view(), name='register'),
    path('auth/<int:id>/<str:token>', views.Auth.as_view(), name='auth'),
    path('login/', views.Login.as_view(), name='login'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('delete/confirm/', views.Delete.as_view(), name='delete'),
    path('superuser/', views.Superuser.as_view(), name='superuser'),
    path('search/email/', views.Email.as_view(), name='email'),
    path('reset/password/', views.Password.as_view(), name='password'),
]