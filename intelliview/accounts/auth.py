from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from jose import jwt
from accounts.models import CustomUser

class SupabaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            # Remove 'Bearer ' from token
            token = auth_header.split(' ')[1]
            
            # Verify and decode the JWT token
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=['HS256']
            )
            
            # Get user from database using Supabase user ID
            user = CustomUser.objects.get(supabase_uid=payload['sub'])
            
            return (user, None)
            
        except jwt.JWTError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e)) 