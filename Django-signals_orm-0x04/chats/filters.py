import django_filters
from django.utils import timezone
from datetime import timedelta
from .models import Message
from django.db.models import Q



class MessageFilter(django_filters.FilterSet):
    sender = django_filters.CharFilter(method='filter_sender') 
    participant_id = django_filters.NumberFilter(field_name='conversation__participants__id', lookup_expr='exact')
    conversation = django_filters.UUIDFilter(field_name='conversation__conversation_id')
    after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    last_hours = django_filters.NumberFilter(method='filter_last_hours')
    
    class Meta:
        model = Message
        fields = ['sender', 'participant_id', 'conversation', 'after', 'before', 'last_hours']

    def filter_last_hours(self, queryset, name, value):
        if value:
            cutoff = timezone.now() - timedelta(hours=value)
            return queryset.filter(sent_at__gte=cutoff)
        return queryset
    
    def filter_sender(self, queryset, name, value):
        # Try filtering by sender__email or conversation__participants__id
        try:
            # Try converting value to int for user ID filtering
            user_id = int(value)
            return queryset.filter(
                Q(sender__email__iexact=value) | Q(conversation__participants__id=user_id)
            )
        except ValueError:
            # If conversion fails, filter only by sender email
            return queryset.filter(sender__email__iexact=value)