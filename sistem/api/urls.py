from django.urls import path
from . import views
from .views import get_users, create_user, user_detail

urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('users/create/', create_user, name='create_user'),
    path('users/<int:pk>', user_detail, name='user_detail'),
    path('inscrever/', views.inscrever_evento, name='api_inscrever_evento'),
    path('eventos/', views.eventos_list, name='api_eventos_list'),
]
