from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from core.models import Tags, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tags-list')


class PublicTagsApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_tags_retrieve_unauthorized(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
        email = 'test@gmail.com',
        name = 'test',
        password = 'test'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_tags_retrieve(self):

        Tags.objects.create(user = self.user, name = 'dessert')
        Tags.objects.create(user = self.user, name = 'vegan')

        res = self.client.get(TAGS_URL)
        tags = Tags.objects.all().order_by('-name')
        tags_serializer = TagSerializer(tags, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, tags_serializer.data)

    def test_tags_limited(self):
        user2 = get_user_model().objects.create_user(
        email = 'test2@gmail.com',
        name = 'test2@gmail.com',
        password = 'test2'
        )
        Tags.objects.create(user = user2, name = 'dessert')
        Tags.objects.create(user = self.user, name = 'vegan')
        tag = Tags.objects.create(user = self.user, name = 'fruity')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[1]['name'], tag.name)
        self.assertEqual(res.data[0]['name'], 'vegan')

    def test_create_tags_successfully(self):
        payload = {
                    'user': self.user.id,
                    'name' : 'abcd tag',
                    }

        res = self.client.post(TAGS_URL,payload)
        exists = Tags.objects.filter(user=self.user,name = payload['name']).exists()

        self.assertTrue(exists)

    def test_create_invalid_tags(self):
        payload = {'name': ''}
        res = self.client.post(TAGS_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tags.objects.create(user=self.user, name='Breakfast')
        tag2 = Tags.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='Coriander',
            time_minuites=10,
            price=5.00,
            user=self.user,
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
