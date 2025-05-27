from django import forms
from .models import TeacherRating

class TeacherRatingForm(forms.ModelForm):
    class Meta:
        model = TeacherRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this teacher...', 'class': 'form-control'}),
        }
