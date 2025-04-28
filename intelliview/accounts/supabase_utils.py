from django.conf import settings
from intelliview.supabase_config import get_supabase_client
from .models import CustomUser

def sync_user_with_supabase(supabase_user):
    """
    Syncs a Supabase user with our Django CustomUser model.
    Creates a new user if they don't exist, updates if they do.
    """
    try:
        user = CustomUser.objects.get(supabase_uid=supabase_user['id'])
        # Update existing user
        user.email = supabase_user['email']
        if 'user_metadata' in supabase_user:
            metadata = supabase_user['user_metadata']
            if 'avatar_url' in metadata:
                user.profile_picture = metadata['avatar_url']
        user.save()
    except CustomUser.DoesNotExist:
        # Create new user
        user = CustomUser.objects.create(
            username=supabase_user['email'],
            email=supabase_user['email'],
            supabase_uid=supabase_user['id']
        )
    return user

def get_supabase_user(token):
    """
    Gets user information from Supabase using the access token.
    """
    supabase = get_supabase_client()
    try:
        user = supabase.auth.get_user(token)
        return user.dict()['user']
    except Exception as e:
        return None

def update_supabase_user(user_id, data):
    """
    Updates user metadata in Supabase.
    """
    supabase = get_supabase_client()
    try:
        response = supabase.auth.admin.update_user_by_id(
            user_id,
            user_metadata=data
        )
        return response
    except Exception as e:
        return None 