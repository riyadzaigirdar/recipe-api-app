from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Tags, Ingredient, Recipe, recipe_image_path

def sample_user(email='testsample',name = 'testsample', password = 'testsample'):
    return get_user_model().objects.create_user(email,name,password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = 'riyad@gmail.com'
        name = 'riyad'
        password = '1234'

        user = get_user_model().objects.create_user(
        email = email,
        name = name,
        password = password
        )
        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_create_new_user(self):
        email = 'riyad@ASD.com'
        user = get_user_model().objects.create_user(email,'1234')
        self.assertEqual(user.email,email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,'1234')

    def test_super_user(self):
        user = get_user_model().objects.create_superuser(
        'riyad@gmail.com',
        'riyad',
        '1234'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self):
        tag = Tags.objects.create(
        user = sample_user(),
        name = 'vegan'
        )

        self.assertEqual(str(tag),tag.name)

    def test_ingredients_str(self):
        ingredients = Ingredient.objects.create(
        name = 'vinegar',
        user = sample_user()
        )

        self.assertEqual(str(ingredients), ingredients.name)

    def test_recipe_string_representation(self):
        recipe = Recipe.objects.create(
        user = sample_user(),
        title = 'fuchuk',
        time_minuites = 10,
        price = 110.85
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_path_uuid(self, mock_uuid):
        uuid = 'test_uuid'
        mock_uuid.return_value = uuid
        file_path = recipe_image_path(None, 'myimage.jpg')

        self.assertEqual(file_path, f'/vol/web/media/{uuid}.jpg')
