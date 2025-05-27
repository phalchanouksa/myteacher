from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile for users that do not have one'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        created_count = 0
        
        for user in users_without_profile:
            # Determine role based on user permissions
            role = 'student'
            if user.is_superuser:
                role = 'admin'
            elif user.is_staff:
                role = 'teacher'
            
            # Create profile
            UserProfile.objects.create(
                user=user,
                role=role
            )
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} user profiles'
            )
        ) 