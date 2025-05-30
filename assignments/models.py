from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import UserProfile

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assignments_given')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - Due: {self.due_date.strftime('%b %d, %Y %H:%M')}"
    
    def is_past_due(self):
        return timezone.now() > self.due_date

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='submissions/%Y/%m/%d/')
    text = models.TextField(blank=True, help_text='Optional text submission')
    grade = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    feedback = models.TextField(blank=True)
    is_plagiarized = models.BooleanField(default=False)
    plagiarism_report = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()}'s submission for {self.assignment.title}"
    
    def get_grade_display(self):
        if self.grade is None:
            return "Not graded"
        return f"{self.grade}/{self.assignment.max_marks}"
