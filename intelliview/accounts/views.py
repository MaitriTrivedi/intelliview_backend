from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, LoginSerializer
from django.contrib.auth import login, logout, authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .supabase_client import (
    create_supabase_user,
    update_supabase_user,
    get_user_by_token,
    delete_supabase_user
)
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes

User = get_user_model()

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
        supabase_user = get_user_by_token(access_token)
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

class UserSyncView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Synchronize a user between Django and Supabase
        """
        email = request.data.get('email')
        supabase_uid = request.data.get('supabase_uid')
        password = request.data.get('password')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            print(f"Syncing user: email={email}, has_password={bool(password)}, has_supabase_uid={bool(supabase_uid)}")
            
            # Try to get existing user from Django
            user = CustomUser.objects.filter(email=email).first()
            
            if user:
                print(f"Found existing user in Django: {user.email}")
                if supabase_uid:
                    user.supabase_uid = supabase_uid
                if password:
                    print("Setting password for existing user")
                    user.set_password(password)
                user.save()
                print(f"Updated user: {user.email}, supabase_uid={user.supabase_uid}")
            else:
                print(f"Creating new user: {email}")
                # Create new user
                username = email.split('@')[0]
                user = CustomUser.objects.create_user(
                    email=email,
                    username=username,
                    password=password,  # This will properly hash the password
                    supabase_uid=supabase_uid,
                    is_active=True
                )
                print(f"Created user: {user.email}, supabase_uid={user.supabase_uid}")
            
            # Return minimal user data
            return Response({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'supabase_uid': user.supabase_uid,
                'is_active': user.is_active
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in UserSyncView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # Hash the password before saving
        user = User.objects.create_user(
            username=serializer.validated_data['email'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', '')
        )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Authenticate a user and return tokens
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                      status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'},
                      status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.check_password(password):
        return Response({'error': 'Invalid credentials'},
                      status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'token': str(refresh.access_token),
        'refresh': str(refresh)
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout a user
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Successfully logged out'})
    except Exception:
        return Response({'error': 'Invalid token'},
                      status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    """
    Get authenticated user details
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
