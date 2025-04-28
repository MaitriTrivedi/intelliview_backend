from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth import login, logout, authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from .supabase_utils import sync_user_with_supabase, get_supabase_user
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created'}, status=201)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    def post(self, request):
        # Your login logic (authenticate the user)
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            # User authenticated successfully, generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'access': access_token,
                'refresh': str(refresh)
            })

        return Response({
            'detail': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out'})
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
        })

class SupabaseAuthCallback(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Handle Supabase authentication callback.
        Expects access_token in request body.
        """
        access_token = request.data.get('access_token')
        if not access_token:
            return Response(
                {'error': 'Access token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get user info from Supabase
        supabase_user = get_supabase_user(access_token)
        if not supabase_user:
            return Response(
                {'error': 'Invalid access token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Sync user with our database
        user = sync_user_with_supabase(supabase_user)
        
        # Return user data
        serializer = UserSerializer(user)
        return Response(serializer.data)
