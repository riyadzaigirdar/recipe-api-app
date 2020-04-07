from django.urls import path
from .views import UserApiView,CustomAuthToken,ManageUserView

app_name = 'user'

urlpatterns = [
    path('create/', UserApiView.as_view(), name='create'),
    path('token/',CustomAuthToken.as_view(),name='token'),
    path('me/',ManageUserView.as_view(),name='me')
]
