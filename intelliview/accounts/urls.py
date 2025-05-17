from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from . import views

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/user/', views.get_user_details, name='user-details'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
