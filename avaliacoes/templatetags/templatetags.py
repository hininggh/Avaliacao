from django import template

register = template.Library()

@register.filter
def get_arquivo_indicador(arquivos_indicadores, indicador):
    return arquivos_indicadores.filter(indicador=indicador).first()

