from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import models
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
        queryset = Resource.objects.all().select_related('author')
        
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
            queryset = sorted(queryset, key=lambda x: x.get_likes_count(), reverse=True)
        else:
            queryset = queryset.order_by(sort)
            
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
        context['comment_form'] = CommentForm()
        context['related_resources'] = Resource.objects.filter(
            models.Q(tags__icontains=self.object.tags) |
            models.Q(resource_type=self.object.resource_type)
        ).exclude(id=self.object.id)[:4]
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
