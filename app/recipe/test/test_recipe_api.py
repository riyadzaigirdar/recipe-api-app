

import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Tags, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def recipe_detail_url(recipe_id):
    return reverse('recipe:recipe-detail',args=[recipe_id])

def sample_tag(user, name='sample tag'):
    return Tags.objects.create(user = user, name = name)

def sample_ingredient(user, name='sample ingredient'):
    return Ingredient.objects.create(user = user, name = name)


def sample_recipe(user, **params):
    defaults = {
        'title':'Khichuri',
        'time_minuites': 30,
        'price': 400.05,
        }

    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApi(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_recipe_url_unauthorized(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApi(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
        'test@gmail.com',
        'test',
        'test12345'
        )
        self.client =APIClient()
        self.client.force_authenticate(self.user)

    def test_recipe_url_authorized(self):
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe_retrieve(self):
        sample_recipe(user = self.user)
        sample_recipe(user = self.user)

        res = self.client.get(RECIPE_URL)
        query_set = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(query_set, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_recipe_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
        'ammu@gmail.com',
        'ammu',
        'ammupass'
        )
        object = sample_recipe(user = self.user)
        sample_recipe(user = user2)
        res = self.client.get(RECIPE_URL)

        query_set = Recipe.objects.all().order_by('-title').filter(user=self.user)
        serializer = RecipeSerializer(query_set, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['title'], object.title)

    def test_recipe_detail_view(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = recipe_detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_successfully(self):
        payload = {
        'user': self.user.id,
        'title': 'labra',
        'time_minuites': 5,
        'price':50.05,

        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_recipe_with_tag_successfully(self):
        tag1 = sample_tag(user = self.user, name='dal')
        tag2 = sample_tag(user = self.user, name='sobji')

        payload = {
            'user': self.user.id,
            'title': 'labra',
            'time_minuites': 5,
            'price':50.05,
            'tags':[tag1.id,tag2.id]
        }

        res = self.client.post(RECIPE_URL, payload)
        tags = Tags.objects.filter(user = self.user)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients_successfully(self):
        ingredients1 = sample_ingredient(user = self.user, name='dal')
        ingredients2 = sample_ingredient(user = self.user, name='sobji')

        payload = {
            'user': self.user.id,
            'title': 'labra',
            'time_minuites': 5,
            'price':50.05,
            'ingredientss':[ingredients1.id,ingredients2.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        ingredients = Ingredient.objects.filter(user = self.user)
        self.assertIn(ingredients1, ingredients)
        self.assertIn(ingredients2, ingredients)

    def test_put_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
                'user': self.user.id,
    			'title': 'Spag',
    			'time_minuites': 25,
    			'price': 5.00,
                'link' : 'aavvfasd',

    		}
        url = recipe_detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minuites, payload['time_minuites'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

    def test_patch_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
    			'title': 'Spag',
    		      }
        url = recipe_detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe_filter_with_tags(self):
        recipe1 = sample_recipe(user=self.user, title='begun')
        recipe2 = sample_recipe(user=self.user, title='Murgi')
        recipe3 = sample_recipe(user=self.user, title='dal')

        tag1 = sample_tag(user=self.user, name='vegan')
        tag2 = sample_tag(user=self.user, name='non-veg')

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(RECIPE_URL, {'tags': f'{tag1.id},{tag2.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # self.assertNotIn(serializer3.data, res.data)

    def test_recipe_filter_with_ingredients(self):
        recipe1 = sample_recipe(user=self.user, title='begun')
        recipe2 = sample_recipe(user=self.user, title='Murgi')
        recipe3 = sample_recipe(user=self.user, title='dal')

        ingredients1 = sample_ingredient(user=self.user, name='salt')
        ingredients2 = sample_ingredient(user=self.user, name='mosla')

        recipe1.ingredients.add(ingredients1)
        recipe2.ingredients.add(ingredients2)

        res = self.client.get(RECIPE_URL, {'ingredients': f'{ingredients1.id},{ingredients2.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # self.assertNotIn(serializer3.data, res.data)


class ImageUploadTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
        'testuser@gmail.com',
        'testuser',
        '1234'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user = self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_successfully(self):
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))



    def test_bad_image_upload(self):
        url = image_upload_url(self.recipe.id)

        res = self.client.post(url, {'image':'noimage'}, format = 'multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
