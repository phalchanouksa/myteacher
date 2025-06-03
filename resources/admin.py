from django.contrib import admin
from .models import Resource, Comment

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'resource_type', 'created_at', 'get_likes_count')
    list_filter = ('resource_type', 'created_at')
    search_fields = ('title', 'description', 'author__user__username')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('resource', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__user__username', 'resource__title')
