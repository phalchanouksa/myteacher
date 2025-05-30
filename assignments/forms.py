from django import forms
from django.utils import timezone
from .models import Assignment, Submission
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'max_marks', 'is_published']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            raise ValidationError(_("Due date cannot be in the past"))
        return due_date

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your submission text here (optional)'}),
        }

class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade', 'feedback', 'is_plagiarized', 'plagiarism_report']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your feedback here'}),
            'plagiarism_report': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Plagiarism report details (if any)'}),
        }
    
    def clean_grade(self):
        grade = self.cleaned_data.get('grade')
        if grade is not None and (grade < 0 or grade > 100):
            raise ValidationError(_("Grade must be between 0 and 100"))
        return grade
