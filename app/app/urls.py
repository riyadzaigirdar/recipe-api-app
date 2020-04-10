
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('api/user/',include('user.urls')),
    path('api/recipe/',include('recipe.urls')),
    path('admin/', admin.site.urls),
]
