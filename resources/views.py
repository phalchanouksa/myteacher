from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import models
from django.db.models import Exists, OuterRef, Count, Value, BooleanField
from django.core.exceptions import PermissionDenied
from .models import Resource, Comment
from .forms import ResourceForm, CommentForm

def test_view(request):
    return HttpResponse("Resources app is working!")

class ResourceListView(ListView):
    model = Resource
    template_name = 'resources/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Resource.objects.all().select_related('author__user') # Efficiently fetch user

        # Annotate with likes_count for sorting and display
        queryset = queryset.annotate(likes_count_annotation=Count('likes'))

        # Annotate with is_liked_by_user for the current user
        if self.request.user.is_authenticated:
            user_profile = self.request.user.profile
            # Check if a like from the current user exists for each resource
            user_likes_subquery = Resource.likes.through.objects.filter(
                resource_id=OuterRef('pk'),
                userprofile_id=user_profile.pk
            )
            queryset = queryset.annotate(
                is_liked_by_user=Exists(user_likes_subquery)
            )
        else:
            # For anonymous users, is_liked_by_user is always False
            queryset = queryset.annotate(is_liked_by_user=Value(False, output_field=BooleanField()))

        # Filter by search query
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                models.Q(title__icontains=q) |
                models.Q(description__icontains=q) |
                models.Q(tags__icontains=q)
            )

        # Filter by type
        resource_type = self.request.GET.get('type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        # Sort options
        sort = self.request.GET.get('sort', '-created_at')
        if sort == 'likes':
            queryset = queryset.order_by('-likes_count_annotation', '-created_at') # Sort by likes, then by date
        elif sort:
            queryset = queryset.order_by(sort)
        # Default sort is already applied if no sort parameter is given and it's not 'likes'

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resource_types'] = Resource.RESOURCE_TYPES
        context['current_type'] = self.request.GET.get('type', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['query'] = self.request.GET.get('q', '')
        return context

class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'resources/resource_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.object # Get the current resource instance

        # Annotate the single resource object
        # We need to re-fetch it or work with the instance to annotate. 
        # For simplicity and consistency with list view, let's re-query and annotate.
        # However, for a single object, direct annotation is more complex than on a queryset.
        # A more straightforward way for a single object is to add these as properties or calculate them here.

        resource_qs = Resource.objects.filter(pk=resource.pk)
        resource_qs = resource_qs.annotate(likes_count_annotation=Count('likes'))

        if self.request.user.is_authenticated:
            user_profile = self.request.user.profile
            user_likes_subquery = Resource.likes.through.objects.filter(
                resource_id=resource.pk, # Use resource.pk directly
                userprofile_id=user_profile.pk
            )
            resource_qs = resource_qs.annotate(
                is_liked_by_user=Exists(user_likes_subquery)
            )
        else:
            resource_qs = resource_qs.annotate(is_liked_by_user=Value(False, output_field=BooleanField()))
        
        # Get the annotated resource instance
        annotated_resource = resource_qs.first()

        context['resource'] = annotated_resource # Override the object with the annotated one
        context['comment_form'] = CommentForm()
        context['related_resources'] = Resource.objects.filter(
            models.Q(tags__icontains=self.object.tags) |
            models.Q(resource_type=self.object.resource_type)
        ).exclude(id=self.object.id).annotate(likes_count_annotation=Count('likes'))[:4] # Also annotate related for consistency if needed
        return context

class ResourceCreateView(LoginRequiredMixin, CreateView):
    model = Resource
    form_class = ResourceForm
    template_name = 'resources/resource_form.html'
    success_url = reverse_lazy('resources:list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        messages.success(self.request, 'Resource created successfully!')
        return super().form_valid(form)

class ResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = 'resources/resource_form.html'
    
    def get_success_url(self):
        return reverse_lazy('resources:detail', kwargs={'pk': self.object.pk})
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user.profile:
            messages.error(request, "You don't have permission to edit this resource.")
            return redirect('resources:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

class ResourceDeleteView(LoginRequiredMixin, DeleteView):
    model = Resource
    success_url = reverse_lazy('resources:list')
    template_name = 'resources/resource_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user.profile:
            messages.error(request, "You don't have permission to delete this resource.")
            return redirect('resources:detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)

class ResourceLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk)
        user_profile = request.user.profile
        
        if user_profile in resource.likes.all():
            resource.likes.remove(user_profile)
            liked = False
        else:
            resource.likes.add(user_profile)
            liked = True
            
        return JsonResponse({
            'liked': liked,
            'likes_count': resource.get_likes_count()
        })

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        resource = get_object_or_404(Resource, pk=self.kwargs['pk'])
        form.instance.resource = resource
        form.instance.author = self.request.user.profile
        response = super().form_valid(form)
        messages.success(self.request, 'Comment added successfully!')
        return response
    
    def get_success_url(self):
        return reverse_lazy('resources:detail', kwargs={'pk': self.kwargs['pk']})
