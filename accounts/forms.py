from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    identifier = forms.CharField(max_length=20, required=False, label='Student ID (auto-generated if empty)')
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Create the profile manually instead of updating the auto-created one
            from .models import UserProfile
            profile_data = {
                'role': 'student',
                'identifier': self.cleaned_data['identifier'],
                'date_of_birth': self.cleaned_data['date_of_birth'],
                'address': self.cleaned_data['address'],
                'phone_number': self.cleaned_data['phone_number']
            }
            
            # Check if profile exists, update it or create a new one
            try:
                profile = UserProfile.objects.get(user=user)
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=user, **profile_data)
                profile.save()
        
        return user

class TeacherCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    identifier = forms.CharField(max_length=20, required=False, label='Teacher ID (auto-generated if empty)')
    department = forms.CharField(max_length=100, required=False)
    designation = forms.CharField(max_length=100, required=False)
    qualification = forms.CharField(max_length=200, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    joining_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    is_staff = forms.BooleanField(required=False, help_text='Designates whether the user can log into this admin site.')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data['is_staff']
        
        if commit:
            user.save()
            
            # Create the profile manually instead of updating the auto-created one
            from .models import UserProfile
            profile_data = {
                'role': 'teacher',
                'identifier': self.cleaned_data['identifier'],
                'department': self.cleaned_data['department'],
                'designation': self.cleaned_data['designation'],
                'qualification': self.cleaned_data['qualification'],
                'date_of_birth': self.cleaned_data['date_of_birth'],
                'address': self.cleaned_data['address'],
                'phone_number': self.cleaned_data['phone_number'],
                'joining_date': self.cleaned_data['joining_date']
            }
            
            # Check if profile exists, update it or create a new one
            try:
                profile = UserProfile.objects.get(user=user)
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=user, **profile_data)
                profile.save()
        
        return user
