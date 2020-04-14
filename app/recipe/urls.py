from recipe.views import TagView, IngriView, RecipeView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
app_name = 'recipe'

router = DefaultRouter()

router.register('tags', TagView)
router.register('ingredients', IngriView)
router.register('recipe', RecipeView)

urlpatterns = [
    path('',include(router.urls))
]
