import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


def recipe_image_path(instance, imagefile):
    image_extension = imagefile.split(".")[-1]
    file_name = f'{uuid.uuid4()}.{image_extension}'
    return os.path.join(settings.MEDIA_ROOT, file_name)


class UserManager(BaseUserManager):
    """docstring for UserManager."""
    def create_user(self,email,name,password=None):
        if not email:
            raise ValueError("User must have email addess")
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,email,name,password):
        user = self.create_user(email,name,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class UserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

class Tags(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE
    )

    def __str__(self):
        return self.name

class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    title = models.CharField(max_length=10)
    time_minuites = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=20, blank=True)
    tags = models.ManyToManyField('Tags')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, blank=True, upload_to = recipe_image_path)

    def __str__(self):
        return self.title
