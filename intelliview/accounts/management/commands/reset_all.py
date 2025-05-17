from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from accounts.supabase_client import get_client

class Command(BaseCommand):
    help = 'Reset all users in both Django and Supabase'

    def handle(self, *args, **options):
        # 1. Delete all Django users
        self.stdout.write('Deleting all Django users...')
        CustomUser.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all Django users'))

        # 2. Delete all Supabase users
        self.stdout.write('Deleting all Supabase users...')
        supabase = get_client()
        try:
            # First try to delete from auth.users
            try:
                supabase.table('auth.users').delete().execute()
                self.stdout.write('Deleted users from auth.users')
            except Exception as e:
                self.stdout.write(f'Note: Could not delete from auth.users: {str(e)}')

            # Try direct SQL deletion from auth schema
            try:
                supabase.rpc('delete_all_users').execute()
                self.stdout.write('Executed RPC to delete all users')
            except Exception as e:
                self.stdout.write(f'Note: Could not execute RPC: {str(e)}')

            # Delete from custom_user table
            try:
                supabase.table('custom_user').delete().execute()
                self.stdout.write('Deleted users from custom_user table')
            except Exception as e:
                self.stdout.write(f'Note: Could not delete from custom_user: {str(e)}')

            # As a final fallback, try to delete individual users through auth API
            try:
                response = supabase.auth.admin.list_users()
                users = response.users if hasattr(response, 'users') else []
                
                for user in users:
                    try:
                        supabase.auth.admin.delete_user(user.id)
                        self.stdout.write(f'Deleted Supabase user through API: {user.email}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Could not delete user {user.email} through API: {str(e)}')
                        )
            except Exception as e:
                self.stdout.write(f'Note: Could not list/delete users through API: {str(e)}')

            self.stdout.write(self.style.SUCCESS('Completed Supabase user deletion attempts'))
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in Supabase operations: {str(e)}')
            )

        self.stdout.write(self.style.SUCCESS('Reset completed successfully!')) 