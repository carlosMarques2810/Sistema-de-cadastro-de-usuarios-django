from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path('', views.accounts, name='accounts'),
    path('register/', views.register, name='register'),
    path('auth/<int:id>/<str:token>', views.auth, name='auth'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('delete/confirm/', views.delete, name='delete'),
    path('logout/', views.logout, name='logout'),
    path('search/email/', views.email, name='email'),
    path('superuser/', views.superuser, name='superuser'),
    path('reset/password/', views.password, name='password'),
]