from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile objects for users that do not have one'

    def handle(self, *args, **options):
        users_without_profile = []
        for user in User.objects.all():
            try:
                # Just checking if the profile exists
                user.profile
            except User.profile.RelatedObjectDoesNotExist:
                users_without_profile.append(user)
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
        
        if not users_without_profile:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {len(users_without_profile)} user profiles'))
