from django import template
import re

register = template.Library()

@register.filter
def youtube_embed_url(url):
    """Convert YouTube video URL to embed URL"""
    if not url:
        return ''
    
    # Regular YouTube URLs
    pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)'
    match = re.match(pattern, url)
    if match:
        return f'https://www.youtube.com/embed/{match.group(1)}'
    
    # Shortened YouTube URLs
    pattern = r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)'
    match = re.match(pattern, url)
    if match:
        return f'https://www.youtube.com/embed/{match.group(1)}'
    
    return url
