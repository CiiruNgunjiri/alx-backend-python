from django.urls import path
from messaging import views

urlpatterns = [
    path('conversations/<uuid:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('delete-account/', views.delete_user, name='delete_user'),
]
