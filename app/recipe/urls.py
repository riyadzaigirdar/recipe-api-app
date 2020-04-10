from recipe.views import RecipeView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('tags', RecipeView)

app_name = 'recipe'

urlpatterns = [
    path('',include(router.urls))
]
