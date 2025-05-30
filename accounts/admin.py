from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from .forms import TeacherCreationForm
from django.db import transaction

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {'fields': ('role', 'identifier')}),
            ('Personal Info', {'fields': ('date_of_birth', 'address', 'phone_number')}),
        ]
        return fieldsets
        
    def get_readonly_fields(self, request, obj=None):
        # Make joining_date read-only in the admin
        return ('joining_date',) if obj else ()

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'profile__role')
    actions = ['make_teacher', 'make_student']
    add_form = UserCreationForm
    
    def add_view(self, request, form_url='', extra_context=None):
        # Use our custom view for adding users
        return redirect('admin:add_teacher')
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'No role'
    get_role.short_description = 'Role'
    
    def make_teacher(self, request, queryset):
        for user in queryset:
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = 'teacher'
            user.is_staff = True
            profile.save()
            user.save()
        self.message_user(request, f"{queryset.count()} user(s) updated to teacher role.")
    make_teacher.short_description = "Mark selected users as teachers"
    
    def make_student(self, request, queryset):
        for user in queryset:
            profile, created = UserProfile.objects.get_or_create(user=user)
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
                with transaction.atomic():
                    # First create and save the user
                    user = form.save(commit=False)
                    user.is_staff = form.cleaned_data.get('is_staff', False)
                    user.save()
                    
                    # Update or create the profile
                    profile_data = {
                        'role': 'teacher',
                        'identifier': form.cleaned_data.get('identifier'),
                        'date_of_birth': form.cleaned_data.get('date_of_birth'),
                        'address': form.cleaned_data.get('address', ''),
                        'phone_number': form.cleaned_data.get('phone_number', '')
                        # joining_date is auto-set to now() by the model's auto_now_add=True
                    }
                    
                    # Update existing profile or create new one
                    UserProfile.objects.update_or_create(
                        user=user,
                        defaults=profile_data
                    )
                
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
