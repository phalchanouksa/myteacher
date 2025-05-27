from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from .forms import TeacherCreationForm

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'
    fieldsets = (
        (None, {'fields': ('role', 'identifier')}),
        ('Personal Info', {'fields': ('date_of_birth', 'address', 'phone_number')}),
        ('Teacher Info', {'fields': ('department', 'designation', 'qualification', 'joining_date'),
                         'classes': ('collapse',),
                         'description': 'Only applicable for teachers'}),
    )

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser')
    actions = ['make_teacher', 'make_student']
    add_form = UserCreationForm
    
    def add_view(self, request, form_url='', extra_context=None):
        # Use our custom view for adding users
        return redirect('admin:add_teacher')
    
    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except:
            return 'No role'
    get_role.short_description = 'Role'
    
    def make_teacher(self, request, queryset):
        for user in queryset:
            try:
                profile = user.profile
            except:
                profile = UserProfile.objects.create(user=user)
            
            profile.role = 'teacher'
            user.is_staff = True
            profile.save()
            user.save()
        self.message_user(request, f"{queryset.count()} user(s) updated to teacher role.")
    make_teacher.short_description = "Mark selected users as teachers"
    
    def make_student(self, request, queryset):
        for user in queryset:
            try:
                profile = user.profile
            except:
                profile = UserProfile.objects.create(user=user)
            
            profile.role = 'student'
            profile.save()
        self.message_user(request, f"{queryset.count()} user(s) updated to student role.")
    make_student.short_description = "Mark selected users as students"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-teacher/', self.admin_site.admin_view(self.add_teacher_view), name='add_teacher'),
        ]
        return custom_urls + urls
    
    def add_teacher_view(self, request):
        if request.method == 'POST':
            form = TeacherCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                
                # Create the profile manually
                profile_data = {
                    'role': 'teacher',
                    'identifier': form.cleaned_data.get('identifier'),
                    'department': form.cleaned_data.get('department', ''),
                    'designation': form.cleaned_data.get('designation', ''),
                    'qualification': form.cleaned_data.get('qualification', ''),
                    'date_of_birth': form.cleaned_data.get('date_of_birth'),
                    'address': form.cleaned_data.get('address', ''),
                    'phone_number': form.cleaned_data.get('phone_number', ''),
                    'joining_date': form.cleaned_data.get('joining_date')
                }
                
                # Create the profile
                profile = UserProfile(user=user, **profile_data)
                profile.save()
                
                # Set staff status
                if form.cleaned_data.get('is_staff'):
                    user.is_staff = True
                    user.save()
                
                self.message_user(request, 'Teacher added successfully')
                return redirect('..')
        else:
            form = TeacherCreationForm()
        
        context = {
            'title': 'Add User',
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/accounts/add_teacher_form.html', context)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
