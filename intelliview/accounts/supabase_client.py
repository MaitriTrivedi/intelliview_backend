from supabase import create_client, Client
from django.conf import settings
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance using settings from Django.
    """
    try:
        if not hasattr(settings, 'SUPABASE_URL') or not hasattr(settings, 'SUPABASE_KEY'):
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in Django settings")
            
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        return supabase
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        raise

def create_supabase_user(email: str, password: str, **additional_data) -> Dict[str, Any]:
    """
    Create a new user in Supabase auth system and public.users table.
    """
    try:
        supabase = get_supabase_client()
        logger.info(f"Creating Supabase user for email: {email}")
        
        # First create the user in auth.users
        try:
            auth_response = supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": additional_data
            })
            
            if not auth_response.user:
                raise ValueError("User creation failed - no user data returned")
                
            user_id = auth_response.user.id
            logger.info(f"Created auth user with ID: {user_id}")
            
            # Now create/update the user in public.users
            user_data = {
                "auth_user_id": user_id,
                "email": email,
                "username": additional_data.get('username', email),
                "first_name": additional_data.get('first_name', ''),
                "last_name": additional_data.get('last_name', ''),
                "is_active": True
            }
            
            response = supabase.from_('users').upsert(user_data).execute()
            logger.info(f"Created public.users entry for user: {email}")
            
            return {
                "user": auth_response.user,
                "public_user": response.data[0] if response.data else None
            }
            
        except Exception as e:
            logger.error(f"Error in create_supabase_user: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Failed to create Supabase user: {str(e)}")
        raise

def get_supabase_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user details from public.users table.
    """
    try:
        supabase = get_supabase_client()
        logger.info(f"Fetching user with ID: {user_id}")
        
        # Get user from public.users table
        response = supabase.from_('users').select('*').eq('auth_user_id', user_id).execute()
        
        if not response.data:
            logger.warning(f"No user found with ID: {user_id}")
            return None
            
        logger.info(f"Found user in public.users")
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Failed to get Supabase user: {str(e)}")
        raise

def update_supabase_user(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update user details in public.users table.
    """
    try:
        supabase = get_supabase_client()
        logger.info(f"Updating user with ID: {user_id}")
        
        # Update user in public.users table
        response = supabase.from_('users').update(update_data).eq('auth_user_id', user_id).execute()
        
        if not response.data:
            logger.warning(f"No user updated with ID: {user_id}")
            return None
            
        # If email is being updated, update auth.users as well
        if 'email' in update_data:
            try:
                supabase.auth.admin.update_user_by_id(
                    user_id,
                    {"email": update_data['email']}
                )
                logger.info(f"Updated email in auth.users for user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to update email in auth.users: {str(e)}")
        
        logger.info(f"Successfully updated user: {user_id}")
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Failed to update Supabase user: {str(e)}")
        raise

def delete_supabase_user(user_id: str) -> None:
    """Delete a user from Supabase"""
    try:
        supabase = get_supabase_client()
        supabase.auth.admin.delete_user(user_id)
    except Exception as e:
        print(f"Error deleting Supabase user: {e}")
        raise

def get_user_by_token(token: str) -> dict:
    """Gets user information from Supabase using the access token."""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        return user.dict()['user']
    except Exception as e:
        return None 