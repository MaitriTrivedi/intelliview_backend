# Placeholder for Supabase client functions
# This file provides dummy implementations for Supabase functions that are imported elsewhere

def create_supabase_user(email, password, **kwargs):
    """Placeholder for create_supabase_user"""
    return {"user": {"id": "dummy-id"}, "public_user": None}

def update_supabase_user(user_id, **data):
    """Placeholder for update_supabase_user"""
    return {"id": user_id, **data}

def get_user_by_token(token):
    """Placeholder for get_user_by_token"""
    return {"id": "dummy-id", "email": "dummy@example.com"}

def delete_supabase_user(user_id):
    """Placeholder for delete_supabase_user"""
    return None

def get_supabase_user(user_id):
    """Placeholder for get_supabase_user"""
    return {"id": user_id, "email": "dummy@example.com"}

def get_supabase_client():
    """Placeholder for get_supabase_client"""
    return None 