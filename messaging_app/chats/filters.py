import django_filters
from .models import Message
from django.utils import timezone
from datetime import timedelta

class MessageFilter(django_filters.FilterSet):
    sender = django_filters.CharFilter(field_name='sender__email', lookup_expr='iexact')
    conversation = django_filters.UUIDFilter(field_name='conversation__conversation_id')
    after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    last_hours = django_filters.NumberFilter(method='filter_last_hours')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'after', 'before']

    def filter_last_hours(self, queryset, name, value):
        if value:
            cutoff = timezone.now() - timedelta(hours=value)
            return queryset.filter(sent_at__gte=cutoff)
        return queryset