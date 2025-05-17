from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from accounts.supabase_utils import create_supabase_user, get_supabase_user, update_supabase_user
import time
import uuid

class Command(BaseCommand):
    help = 'Synchronize users between Django and Supabase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-reset',
            action='store_true',
            help='Force reset Supabase UIDs and recreate users',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting user synchronization...')
        force_reset = options['force_reset']
        
        # Get all Django users
        users = CustomUser.objects.all()
        
        for user in users:
            self.stdout.write(f'Processing user: {user.email}')
            
            try:
                if user.supabase_uid and not force_reset:
                    # Try to get user from Supabase
                    try:
                        supabase_user = get_supabase_user(user.supabase_uid)
                        if supabase_user:
                            self.stdout.write(f'User {user.email} exists in Supabase')
                            continue
                    except Exception as e:
                        self.stdout.write(f'Error checking Supabase user: {str(e)}')
                    
                    self.stdout.write(f'User {user.email} not found in Supabase, will recreate')
                    user.supabase_uid = None
                
                # Create new Supabase user
                self.stdout.write(f'Creating user {user.email} in Supabase')
                temp_password = f'temp_{uuid.uuid4().hex[:8]}'
                try:
                    supabase_data = create_supabase_user(user.email, temp_password)
                    if supabase_data and 'user' in supabase_data and 'id' in supabase_data['user']:
                        user.supabase_uid = supabase_data['user']['id']
                        user.save()
                        self.stdout.write(f'Created Supabase user for {user.email} with ID {user.supabase_uid}')
                        
                        # Update user metadata
                        update_supabase_user(user.supabase_uid, {
                            'email': user.email,
                            'user_metadata': {
                                'django_id': user.id,
                                'username': user.username,
                                'is_staff': user.is_staff,
                                'is_superuser': user.is_superuser
                            }
                        })
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to create Supabase user for {user.email}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating Supabase user for {user.email}: {str(e)}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing user {user.email}: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS('User synchronization completed')) 