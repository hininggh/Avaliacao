from django.db import models

from django.db import models
from contas.models import CustomUser

class Avaliacao(models.Model):
    nome = models.CharField(max_length=255)
    inscricao = models.CharField(max_length=255)
    data_criacao = models.DateTimeField(auto_now_add=True)
    distribuidor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='avaliacoes_criadas', limit_choices_to={'user_type': 'distribuidor'})
    avaliadores = models.ManyToManyField(CustomUser, related_name='avaliacoes', limit_choices_to={'user_type': 'avaliador'})

    def __str__(self):
        return self.nome

class Indicador(models.Model):
    DIMENSOES = (
        ('Organização Didático-Pedagógico', 'Organização Didático-Pedagógico'),
        ('Corpo Docente e Tutorial', 'Corpo Docente e Tutorial'),
        ('Infraestrutura', 'Infraestrutura'),
    )
    nome = models.CharField(max_length=255)
    dimensao = models.CharField(max_length=255, choices=DIMENSOES)
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='indicadores')

    def __str__(self):
        return self.nome

class ArquivoIndicador(models.Model):
    arquivo = models.FileField(upload_to='arquivos_indicadores/')
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, related_name='arquivos')
    avaliador = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='arquivos_indicadores', limit_choices_to={'user_type': 'avaliador'})

    class Meta:
        unique_together = ('indicador', 'avaliador')


class CapaAvaliacao(models.Model):
    capa = models.FileField(upload_to='capas_avaliacoes/')
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='capas')
    avaliador = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='capas_avaliacoes', limit_choices_to={'user_type': 'avaliador'})