from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@londonappdev.com',
            name = 'admin',
            password='password123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@londonappdev.com',
            password='password123',
            name='Test User Full Name',
        )

    def test_users_listed(self):
        """Test that users are listed on the user page"""
        url = reverse('admin:core_usermodel_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change(self):
        url = reverse('admin:core_usermodel_change',args={self.user.id})
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res,self.user.email)
        # or
        self.assertEqual(res.status_code,200)

    def test_create_user(self):
        url = reverse("admin:core_usermodel_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code,200)
