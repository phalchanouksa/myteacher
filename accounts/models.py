from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from datetime import datetime

# Create your models here.
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    identifier = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    def generate_identifier(self):
        # Auto-generate identifier
        year = datetime.now().strftime("%y")
        if self.role == 'student':
            prefix = f"S{year}"
        elif self.role == 'teacher':
            prefix = f"T{year}"
        else:
            prefix = f"A{year}"
        
        # Generate a unique random suffix (4 digits)
        random_suffix = str(uuid.uuid4().int)[:4]
        return f"{prefix}{random_suffix}"
    
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    joining_date = models.DateField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Auto-generate identifier if not provided
        if not self.identifier:
            self.identifier = self.generate_identifier()
            
            # Make sure the identifier is unique
            while UserProfile.objects.filter(identifier=self.identifier).exists():
                self.identifier = self.generate_identifier()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.role})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Determine role based on user permissions
        role = 'student'
        if instance.is_superuser:
            role = 'admin'
        elif instance.is_staff:
            role = 'teacher'
        
        UserProfile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        role = 'student'
        if instance.is_superuser:
            role = 'admin'
        elif instance.is_staff:
            role = 'teacher'
        UserProfile.objects.create(user=instance, role=role)
