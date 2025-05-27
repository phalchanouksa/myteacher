from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import UserProfile
from .models import TeacherRating
from .forms import TeacherRatingForm
from django.db.models import Avg

# Create your views here.
@login_required
def teacher_list(request):
    # Get all teachers
    teachers = UserProfile.objects.filter(role='teacher')
    
    # Add average rating to each teacher
    for teacher in teachers:
        teacher.avg_rating = TeacherRating.objects.filter(teacher=teacher).aggregate(Avg('rating'))['rating__avg']
        teacher.rating_count = TeacherRating.objects.filter(teacher=teacher).count()
    
    return render(request, 'ratings/teacher_list.html', {'teachers': teachers})

@login_required
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(UserProfile, id=teacher_id, role='teacher')
    ratings = TeacherRating.objects.filter(teacher=teacher)
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    
    # Check if the current user has already rated this teacher
    current_user_profile = request.user.profile
    user_rating = None
    
    if current_user_profile.role == 'student':
        try:
            user_rating = TeacherRating.objects.get(teacher=teacher, student=current_user_profile)
            form = TeacherRatingForm(instance=user_rating)
        except TeacherRating.DoesNotExist:
            form = TeacherRatingForm()
    else:
        form = None
    
    if request.method == 'POST' and current_user_profile.role == 'student':
        if user_rating:
            form = TeacherRatingForm(request.POST, instance=user_rating)
        else:
            form = TeacherRatingForm(request.POST)
        
        if form.is_valid():
            rating = form.save(commit=False)
            rating.teacher = teacher
            rating.student = current_user_profile
            rating.save()
            messages.success(request, 'Your rating has been submitted!')
            return redirect('teacher_detail', teacher_id=teacher.id)
    
    context = {
        'teacher': teacher,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'form': form,
        'user_has_rated': user_rating is not None
    }
    
    return render(request, 'ratings/teacher_detail.html', context)
