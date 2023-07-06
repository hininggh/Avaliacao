from django.urls import path
from . import views

app_name = 'contas'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.signup, name='cadastro'),
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    path('detalhes_usuario/<int:pk>/', views.detalhes_usuario, name='detalhes_usuario'),
    path('detalhes_usuario/', views.detalhes_usuario, name='detalhes_usuario')
]
