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
from django.urls import path, include
from login import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #Admin site
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', views.base, name = "home_page"),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout, name='logout'),
    #url para usuario
    path('home_organizador/', views.base, name='home_organizador'),
    path('cadastro/', views.cadastro_usuario, name='cadastro'),
    path('usuarios/', views.editar_usuario, name='edit_user'),
    path('usuarios/totais', views.ver_usuario, name='usuario'),
    #url para eventos
    path('cadastro_evento/', views.cadastro_eventos, name='cadastro_evento'),
    path('editar_evento/<int:pk>/', views.editar_evento, name='editar_evento'),
    path('deletar_evento/<int:pk>/', views.deletar_evento, name='deletar_evento'),
    path('eventos/', views.todos_eventos, name='eventos'),
    path("eventos_disp/", views.eventos_disponiveis, name="inscricao_evento_disp"),
    path('eventos/inscricao/<int:evento_id>/', views.inscricao_evento, name='inscricao_evento'),
    path("home_inscricao/", views.home_inscricao, name = "list_inscricao"),
    #url para certificados
    path('emitir_certificados/<int:evento_id>/', views.emitir_certificados, name='emitir_certificados'),
    path('certificados/', views.meus_certificados, name='certificados'),
    path('ver_certificados/<int:id_carrinho>/', views.ver_certificados, name='ver_certificados'),
    #url para logs
    path('logs/', views.logs, name='logs'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
