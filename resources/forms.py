from django import forms
from .models import Resource, Comment

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['title', 'description', 'file', 'external_link', 'resource_type', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a descriptive title',
                'autofocus': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what this resource is about and how it can help others...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.ppt,.pptx,.txt,.py,.js,.html,.css,.jpg,.png,.mp4'
            }),
            'external_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://...'
            }),
            'resource_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., python, django, web development'
            })
        }
        help_texts = {
            'tags': 'Enter tags separated by commas to help others find your resource'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 20:
            raise forms.ValidationError('Description must be at least 20 characters long.')
        return description

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if len(tags) > 255:
            raise forms.ValidationError('Tags input is too long. Please keep it under 255 characters.')
        return ','.join([tag.strip() for tag in tags.split(',') if tag.strip()])

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        external_link = cleaned_data.get('external_link')
        resource_type = cleaned_data.get('resource_type')
        
        if not file and not external_link:
            raise forms.ValidationError('You must provide either a file or an external link.')
            
        if file and resource_type == 'link':
            raise forms.ValidationError('Cannot upload a file for link-type resources.')
            
        if external_link and resource_type in ['document', 'video']:
            if resource_type == 'document' and 'drive.google.com' not in external_link:
                raise forms.ValidationError('For document-type resources with links, please use Google Drive.')
            if resource_type == 'video' and 'youtube.com' not in external_link and 'youtu.be' not in external_link:
                raise forms.ValidationError('For video-type resources with links, please use YouTube.')
            
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts about this resource...',
                'style': 'resize: vertical;'
            }),
        }
        
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 10:
            raise forms.ValidationError('Comment must be at least 10 characters long.')
        return content
