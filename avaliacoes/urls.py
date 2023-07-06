from django.urls import path
from . import views

app_name = 'avaliacoes'


urlpatterns = [
    path('', views.home, name='home'),
    path('criar_avaliacao/', views.criar_avaliacao, name='criar_avaliacao'),
    path('detalhes_avaliacao/<int:avaliacao_id>/', views.detalhes_avaliacao, name='detalhes_avaliacao'),
    path('excluir_avaliacao/<int:avaliacao_id>/', views.excluir_avaliacao, name='excluir_avaliacao'),
    path('editar_avaliacao/<int:avaliacao_id>/', views.editar_avaliacao, name='editar_avaliacao'),
    path('avaliador_detalhes_avaliacao/<int:avaliacao_id>/', views.avaliador_detalhes_avaliacao, name='avaliador_detalhes_avaliacao'),
    path('distribuidor_detalhes_avaliacao/<int:avaliacao_id>/', views.distribuidor_detalhes_avaliacao, name='distribuidor_detalhes_avaliacao'),
    path('distribuidor_detalhes_avaliacao_arquivos/<int:avaliador_id>/<int:avaliacao_id>/', views.distribuidor_detalhes_avaliacao_arquivos, name='distribuidor_detalhes_avaliacao_arquivos'),
    path('criar_indicador/<int:avaliacao_id>/', views.criar_indicador, name='criar_indicador'),
    path('exibir_criar_indicador/<int:avaliacao_id>/', views.exibir_criar_indicador, name='exibir_criar_indicador'),
    path('excluir_indicador/<int:indicador_id>/', views.excluir_indicador, name='excluir_indicador'),
    path('editar_indicador/<int:indicador_id>/', views.editar_indicador, name='editar_indicador'),
    path('copiar_indicadores/<int:avaliacao_id>/', views.copiar_indicadores, name='copiar_indicadores'),
    path('exibir_copiar_indicadores/<int:avaliacao_id>/', views.exibir_copiar_indicadores,
         name='exibir_copiar_indicadores'),
    path('listar_avaliadores/', views.listar_avaliadores, name='listar_avaliadores'),
    path('enviar_capa/<int:avaliacao_id>/', views.enviar_capa, name='enviar_capa'),
    path('substituir_capa/<int:capa_id>/', views.substituir_capa, name='substituir_capa'),
    path('apagar_capa/<int:capa_id>/', views.apagar_capa, name='apagar_capa'),
    path('baixar_capa/<int:capa_id>/', views.baixar_capa, name='baixar_capa'),
    path('enviar_arquivo/<int:indicador_id>/', views.enviar_arquivo, name='enviar_arquivo'),
    path('substituir_arquivo/<int:arquivo_id>/', views.substituir_arquivo, name='substituir_arquivo'),
    path('apagar_arquivo/<int:arquivo_id>/', views.apagar_arquivo, name='apagar_arquivo'),
    path('baixar_arquivo/<int:arquivo_id>/', views.baixar_arquivo, name='baixar_arquivo'),
    path('baixar_arquivo_distribuidor/<int:arquivo_id>/', views.baixar_arquivo_distribuidor, name='baixar_arquivo_distribuidor'),
]
