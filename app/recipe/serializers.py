from rest_framework import serializers

from core.models import Tags, Ingredient, Recipe

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ['id', 'name']
        read_only_fields = ['id']

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class RecipeSerializer(serializers.ModelSerializer):

    ingredients = serializers.PrimaryKeyRelatedField(
            many = True,
            queryset = Ingredient.objects.all()
            )

    tags = serializers.PrimaryKeyRelatedField(
            many = True,
            queryset = Tags.objects.all()
            )

    class Meta:
        model = Recipe
        fields = ['id', 'user', 'tags', 'ingredients', 'title', 'time_minuites', 'price', 'link']
        read_only_fields = ['id']

class RecipeDetailSerializer(RecipeSerializer):

    ingredients = IngredientSerializer(many = True, read_only = True)
    tags = TagSerializer(many = True, read_only = True)

class RecipeImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
