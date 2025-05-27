from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib import messages
from .models import ChatMessage
from accounts.models import UserProfile

# Create your views here.

@login_required
def inbox(request):
    user_profile = request.user.profile
    # Get unique chat partners
    sent_to = ChatMessage.objects.filter(sender=user_profile).values_list('receiver', flat=True).distinct()
    received_from = ChatMessage.objects.filter(receiver=user_profile).values_list('sender', flat=True).distinct()
    
    # Combine and get unique partner profiles
    partner_ids = set(list(sent_to) + list(received_from))
    chat_partners = UserProfile.objects.filter(id__in=partner_ids)
    
    context = {
        'chat_partners': chat_partners,
        'user_profile': user_profile
    }
    return render(request, 'chat/inbox.html', context)

@login_required
def chat_detail(request, partner_id):
    user_profile = request.user.profile
    partner = get_object_or_404(UserProfile, id=partner_id)
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            # Create new message
            ChatMessage.objects.create(
                sender=user_profile,
                receiver=partner,
                message=message_text
            )
            return redirect('chat_detail', partner_id=partner_id)
    
    # Mark messages as read
    ChatMessage.objects.filter(
        sender=partner,
        receiver=user_profile,
        is_read=False
    ).update(is_read=True)
    
    # Get conversation messages
    chat_messages = ChatMessage.objects.filter(
        (Q(sender=user_profile) & Q(receiver=partner)) |
        (Q(sender=partner) & Q(receiver=user_profile))
    ).order_by('timestamp')
    
    context = {
        'partner': partner,
        'chat_messages': chat_messages,
        'user_profile': user_profile
    }
    return render(request, 'chat/chat_detail.html', context)

@login_required
def get_unread_count(request):
    user_profile = request.user.profile
    # Count unique senders who have sent unread messages
    unread_count = ChatMessage.objects.filter(
        receiver=user_profile,
        is_read=False
    ).values('sender').distinct().count()
    
    return JsonResponse({'unread_count': unread_count})
