"""
URL configuration for sistem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from login import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.base, name = "home_page"),
    path('home_organizador/', views.base, name='home_organizador'),
    path('cadastro/', views.cadastro_usuario, name='cadastro'),
    path('login/', views.login_user, name='login'),
    path('usuarios/', views.editar_usuario, name='edit_user'),
    path('usuarios/totais', views.ver_usuario, name='usuario'),
    path('cadastro_evento/', views.cadastro_eventos, name='cadastro_evento'),
    path('eventos/', views.todos_eventos, name='eventos'),
    path('eventos/inscricao', views.inscricao_evento, name='inscricao_eventos'),
    path("home_inscricao/", views.home_inscricao, name = "list_inscricao"),
]
