from django.urls import path, include
from django.contrib.auth.decorators import user_passes_test
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls')),
]