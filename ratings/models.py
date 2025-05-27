from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import UserProfile
from django.utils import timezone

# Create your models here.
class TeacherRating(models.Model):
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='ratings', limit_choices_to={'role': 'teacher'})
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='given_ratings', limit_choices_to={'role': 'student'})
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('teacher', 'student')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.user.username}'s rating for {self.teacher.user.username}: {self.rating}/5"
