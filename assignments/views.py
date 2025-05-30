from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse, FileResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm
from accounts.models import UserProfile

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = 'assignments/assignment_list.html'
    context_object_name = 'assignments'
    
    def get_queryset(self):
        user = self.request.user.profile
        if user.role == 'teacher':
            return Assignment.objects.filter(teacher=user).order_by('-created_at')
        else:
            return Assignment.objects.filter(is_published=True).order_by('-created_at')

class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = 'assignments/assignment_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.profile
        
        if user.role == 'student':
            context['submission'] = Submission.objects.filter(
                assignment=self.object,
                student=user
            ).first()
        else:
            context['submissions'] = self.object.submissions.all()
            
        return context

class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.profile
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Assignment created successfully!')
        return reverse_lazy('assignments:assignment-detail', kwargs={'pk': self.object.pk})
        
    def test_func(self):
        return self.request.user.profile.role == 'teacher'

class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user.profile
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Assignment updated successfully!')
        return reverse_lazy('assignments:assignment-detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        assignment = self.get_object()
        return self.request.user.profile == assignment.teacher

class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Assignment
    template_name = 'assignments/assignment_confirm_delete.html'
    success_url = reverse_lazy('assignments:assignment-list')
    
    def test_func(self):
        assignment = self.get_object()
        return self.request.user.profile == assignment.teacher

@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, is_published=True)
    user = request.user.profile
    
    if user.role != 'student':
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignments:assignment-detail', pk=pk)
    
    # Check if submission already exists
    submission = Submission.objects.filter(assignment=assignment, student=user).first()
    
    # If submission exists, prevent editing
    if submission:
        messages.error(request, 'You have already submitted this assignment. Multiple submissions are not allowed.')
        return redirect('assignments:assignment-detail', pk=pk)
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = user
            
            # Here you would typically call the plagiarism check API
            # For now, we'll just set a placeholder
            submission.is_plagiarized = False
            submission.plagiarism_report = 'Plagiarism check not implemented yet'
            submission.save()
            
            messages.success(request, 'Your assignment has been submitted successfully!')
            return redirect('assignments:assignment-detail', pk=pk)
    else:
        form = SubmissionForm()
    
    return render(request, 'assignments/submit_assignment.html', {
        'form': form,
        'assignment': assignment,
        'submission': None  # No submission exists yet
    })

@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    
    if request.user.profile != submission.assignment.teacher:
        messages.error(request, 'You are not authorized to grade this submission.')
        return redirect('assignments:assignment-detail', pk=submission.assignment.pk)
    
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade submitted successfully!')
            return redirect('assignments:assignment-detail', pk=submission.assignment.pk)
    else:
        form = GradeSubmissionForm(instance=submission)
    
    return render(request, 'assignments/grade_submission.html', {
        'form': form,
        'submission': submission,
        'assignment': submission.assignment
    })

@login_required
def download_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    user = request.user.profile
    
    # Only the student who submitted, the teacher, or an admin can download
    if user not in [submission.student, submission.assignment.teacher] and not user.user.is_staff:
        messages.error(request, 'You are not authorized to view this submission.')
        return redirect('assignments:assignment-detail', pk=submission.assignment.pk)
    
    if not submission.file:
        messages.error(request, 'No file found for this submission.')
        return redirect('assignments:assignment-detail', pk=submission.assignment.pk)
    
    return FileResponse(submission.file.open('rb'), as_attachment=True, filename=submission.file.name.split('/')[-1])

def check_plagiarism(submission):
    """
    Placeholder for plagiarism check integration.
    In a real implementation, this would call an external API like Turnitin, etc.
    """
    # This is a placeholder implementation
    return {
        'is_plagiarized': False,
        'score': 0,
        'report': 'Plagiarism check not implemented. This is a placeholder.'
    }
