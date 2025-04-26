from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ProfileView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view()),  # Our custom endpoint
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh
    path('profile/', ProfileView.as_view(), name='profile'),
]
