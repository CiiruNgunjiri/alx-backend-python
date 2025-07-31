from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib import messages
from messaging.models import Message
from chats.models import Conversation

# Assuming you have a conversation instance:
def get_threaded_messages(messages):
    """
    Build nested dict for messages and their replies.
    """
    message_dict = {}
    for msg in messages:
        message_dict[msg.message_id] = {'message': msg, 'replies': []}

    root_messages = []

    for msg in messages:
        if msg.parent_message is None:
            root_messages.append(message_dict[msg.message_id])
        else:
            parent_id = msg.parent_message.message_id
            if parent_id in message_dict:
                message_dict[parent_id]['replies'].append(message_dict[msg.message_id])

    return root_messages

@cache_page(60)
def conversation_detail(request, conversation_id):
    # Get the conversation or 404
    conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
    
    # Fetch all messages for this conversation, prefetch sender, receiver, parent, and replies
    messages_qs = Message.objects.filter(conversation=conversation).select_related(
        'sender', 'receiver', 'parent_message'
    ).prefetch_related('replies').order_by('sent_at')

    # Build threaded structure
    threaded_messages = get_threaded_messages(messages_qs)

    context = {
        'conversation': conversation,
        'threaded_messages': threaded_messages,
    }

    return render(request, 'messaging/conversation_detail.html', context)


@login_required
def delete_user(request):
    user = request.user
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')  # change 'home' to your homepage url name
    # For GET, render a confirmation page or just redirect
    # Or use a template for confirmation if needed
    return redirect('profile')  # or show confirmation page

def inbox(request):
    user = request.user
    # Using custom manager to get unread messages for the user,
    # retrieving only the specified fields with `.only()`
    unread_messages = Message.unread.for_user(user)

    context = {
        'unread_messages': unread_messages,
    }
    return render(request, 'messaging/inbox.html', context)