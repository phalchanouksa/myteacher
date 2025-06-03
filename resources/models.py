from django.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from accounts.models import UserProfile

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('document', 'Document'),
        ('video', 'Video'),
        ('link', 'External Link'),
        ('presentation', 'Presentation'),
        ('code', 'Code Snippet'),
        ('other', 'Other'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(
        help_text="Describe what this resource is about and how it can help others."
    )
    file = models.FileField(
        upload_to='resources/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'py', 'js', 'html', 'css', 'jpg', 'png', 'mp4']
        )],
        help_text="Upload a file (PDF, Word, PPT, code files, or media)"
    )
    external_link = models.URLField(
        blank=True,
        null=True,
        help_text="Add a link to an external resource (e.g., YouTube video, website)"
    )
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Enter tags separated by commas (e.g., python, django, web development)"
    )
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(UserProfile, related_name='liked_resources', blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_likes_count(self):
        return self.likes.count()
    
    def get_absolute_url(self):
        return reverse('resources:detail', kwargs={'pk': self.pk})
    
    def get_file_type(self):
        if self.file:
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['pdf', 'doc', 'docx']:
                return 'document'
            elif ext in ['jpg', 'png', 'gif']:
                return 'image'
            elif ext in ['mp4', 'mov']:
                return 'video'
            elif ext in ['py', 'js', 'html', 'css']:
                return 'code'
        return None
    
    def get_tag_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

class Comment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Comment by {self.author.user.get_full_name()} on {self.resource.title}'
