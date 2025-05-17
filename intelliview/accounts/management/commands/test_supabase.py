from django.core.management.base import BaseCommand
from accounts.supabase_client import get_client
from django.conf import settings

class Command(BaseCommand):
    help = 'Test Supabase connection and configuration'

    def handle(self, *args, **options):
        self.stdout.write('Testing Supabase connection...')
        
        # 1. Check settings
        self.stdout.write('\nChecking Supabase settings:')
        self.stdout.write(f'SUPABASE_URL: {"✓ Set" if settings.SUPABASE_URL else "✗ Missing"}')
        self.stdout.write(f'SUPABASE_KEY: {"✓ Set" if settings.SUPABASE_KEY else "✗ Missing"}')
        
        # 2. Test connection
        try:
            supabase = get_client()
            self.stdout.write('\nTesting Supabase client:')
            self.stdout.write('✓ Client initialized successfully')
            
            # 3. Test auth API
            try:
                response = supabase.auth.admin.list_users()
                self.stdout.write('✓ Auth API working (list_users successful)')
                self.stdout.write(f'Found {len(response.users) if hasattr(response, "users") else 0} users')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Auth API error: {str(e)}'))
            
            # 4. Test database connection
            try:
                response = supabase.from_('auth.users').select("*").limit(1).execute()
                self.stdout.write('✓ Database connection working')
            except Exception as e:
                # Try alternative table name
                try:
                    response = supabase.from_('users').select("*").limit(1).execute()
                    self.stdout.write('✓ Database connection working (using users table)')
                except Exception as e2:
                    self.stdout.write(self.style.ERROR(f'✗ Database error: {str(e2)}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Failed to initialize Supabase client: {str(e)}'))
            return
        
        self.stdout.write(self.style.SUCCESS('\nSupabase connection test completed')) 