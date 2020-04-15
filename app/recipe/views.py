from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Tags, Ingredient, Recipe
from recipe.serializers import TagSerializer, IngredientSerializer, RecipeSerializer, RecipeDetailSerializer, RecipeImageSerializer

class BaseRecipeView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        assigned_only = bool(self.request.query_params.get('assigned_only'))

        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user =self.request.user)


class TagView(BaseRecipeView):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngriView(BaseRecipeView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def _get_params_to_int(self, qs):
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        tag_req = self.request.query_params.get('tags')
        ing_req = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tag_req:
            tags_ids = self._get_params_to_int(tag_req)
            queryset = queryset.filter(tags__id__in = tags_ids)
        if ing_req:
            ings_ids = self._get_params_to_int(ing_req)
            queryset = queryset.filter(ingredients__id__in = ings_ids)

        return queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self,request,pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(
        recipe,
        data = request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
