from django.test import TestCase
from django.contrib.auth import get_user_model

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
