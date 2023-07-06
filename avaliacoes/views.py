from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Avaliacao, Indicador, ArquivoIndicador, CapaAvaliacao
from .forms import AvaliacaoForm, IndicadorForm, ArquivoIndicadorForm, CapaAvaliacaoForm
from PyPDF2 import PdfFileMerger
from contas.models import CustomUser
from django.http import HttpResponse
from django.http import FileResponse


@login_required
def home(request):
    if request.user.user_type == 'distribuidor':
        avaliacoes = Avaliacao.objects.filter(distribuidor=request.user)
    else:
        avaliacoes = request.user.avaliacoes.all()
    return render(request, 'avaliacoes/home.html', {'avaliacoes': avaliacoes})

#avaliações
@login_required
def criar_avaliacao(request):
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.distribuidor = request.user
            avaliacao.save()
            form.save_m2m()
            messages.success(request, 'Avaliação criada com sucesso!')
            return redirect('avaliacoes:exibir_criar_indicador', avaliacao.id)
    else:
        form = AvaliacaoForm()
    avaliacoes = Avaliacao.objects.filter(distribuidor=request.user)
    return render(request, 'avaliacoes/criar_avaliacao.html', {'form': form, 'avaliacoes': avaliacoes})

@login_required
def detalhes_avaliacao(request, avaliacao_id, avaliador_id=None):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.user.user_type == 'distribuidor' and request.user != avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para ver os detalhes desta avaliação.')
        return redirect('avaliacoes:home')
    if request.user.user_type == 'avaliador' and request.user not in avaliacao.avaliadores.all():
        messages.error(request, 'Você não tem permissão para ver os detalhes desta avaliação.')
        return redirect('avaliacoes:home')

    avaliador_selecionado = None
    if request.user.user_type == 'distribuidor' and avaliador_id:
        avaliador_selecionado = get_object_or_404(CustomUser, id=avaliador_id, user_type='avaliador', avaliacoes=avaliacao)

    indicadores_por_dimensao = {}
    for dimensao in Indicador.DIMENSOES:
        indicadores_por_dimensao[dimensao[0]] = Indicador.objects.filter(avaliacao=avaliacao, dimensao=dimensao[0])

    arquivos_por_indicador = {}
    if avaliador_selecionado:
        arquivos_por_indicador = ArquivoIndicador.objects.filter(indicador__avaliacao=avaliacao, avaliador=avaliador_selecionado).select_related('indicador')

    capa_enviada = None
    if request.user.user_type == 'avaliador':
        capa_enviada = CapaAvaliacao.objects.filter(avaliacao=avaliacao, avaliador=request.user).first()

    if request.user.user_type == 'distribuidor':
        template_name = 'avaliacoes/distribuidor_detalhes_avaliacao.html'
    else:
        template_name = 'avaliacoes/avaliador_detalhes_avaliacao.html'

    return render(request, template_name, {
        'avaliacao': avaliacao,
        'indicadores_por_dimensao': indicadores_por_dimensao,
        'avaliador_selecionado': avaliador_selecionado,
        'arquivos_por_indicador': arquivos_por_indicador,
        'capa_enviada': capa_enviada,
    })


@login_required
def excluir_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.user != avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para excluir esta avaliação.')
        return redirect('avaliacoes:home')
    if request.method == 'POST':
        # Excluir arquivos e capas relacionados
        for indicador in avaliacao.indicadores.all():
            for arquivo in indicador.arquivos.all():
                arquivo.delete()
        for capa in avaliacao.capas.all():
            capa.delete()
        # Excluir avaliação
        avaliacao.delete()
        messages.success(request, 'Avaliação excluída com sucesso!')
        return redirect('avaliacoes:home')
    return render(request, 'avaliacoes/excluir_avaliacao.html', {'avaliacao': avaliacao})


@login_required
def editar_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.user != avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para editar esta avaliação.')
        return redirect('avaliacoes:home')
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=avaliacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Avaliação atualizada com sucesso!')
            return redirect('avaliacoes:detalhes_avaliacao', avaliacao.id)
    else:
        form = AvaliacaoForm(instance=avaliacao)
    indicadores_por_dimensao = {}
    for dimensao in Indicador.DIMENSOES:
        indicadores_por_dimensao[dimensao[0]] = Indicador.objects.filter(avaliacao=avaliacao, dimensao=dimensao[0])
    return render(request, 'avaliacoes/editar_avaliacao.html', {'form': form, 'avaliacao': avaliacao, 'indicadores_por_dimensao': indicadores_por_dimensao})


def listar_avaliacoes(request):
    if request.user.user_type == 'distribuidor':
        avaliacoes = Avaliacao.objects.filter(distribuidor=request.user)
    elif request.user.user_type == 'avaliador':
        avaliacoes = Avaliacao.objects.filter(avaliadores=request.user)
    else:
        avaliacoes = Avaliacao.objects.none()
    return avaliacoes


def listar_avaliadores(request):
    avaliadores = CustomUser.objects.filter(user_type='avaliador')
    return render(request, 'avaliacoes/listar_avaliadores.html', {'avaliadores': avaliadores})

@login_required
def avaliador_detalhes_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    capa = CapaAvaliacao.objects.filter(avaliacao=avaliacao, avaliador=request.user).first()
    indicadores = Indicador.objects.filter(avaliacao=avaliacao)
    arquivos_indicadores = ArquivoIndicador.objects.filter(indicador__in=indicadores, avaliador=request.user)

    context = {
        'avaliacao': avaliacao,
        'capa': capa,
        'indicadores': indicadores,
        'arquivos_indicadores': arquivos_indicadores,
    }
    return render(request, 'avaliacoes/avaliador_detalhes_avaliacao.html', context)



@login_required
def distribuidor_detalhes_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    indicadores = Indicador.objects.filter(avaliacao=avaliacao)
    avaliadores = CustomUser.objects.filter(avaliacoes=avaliacao)

    # Agrupa os indicadores por dimensão
    indicadores_por_dimensao = {}
    for indicador in indicadores:
        if indicador.dimensao not in indicadores_por_dimensao:
            indicadores_por_dimensao[indicador.dimensao] = []
        indicadores_por_dimensao[indicador.dimensao].append(indicador)

    context = {
        'avaliacao': avaliacao,
        'indicadores_por_dimensao': indicadores_por_dimensao,
        'avaliadores': avaliadores,
    }
    return render(request, 'avaliacoes/distribuidor_detalhes_avaliacao.html', context)

@login_required
def distribuidor_detalhes_avaliacao_arquivos(request, avaliador_id, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    avaliador = get_object_or_404(CustomUser, id=avaliador_id)
    indicadores = Indicador.objects.filter(avaliacao=avaliacao)
    arquivos = ArquivoIndicador.objects.filter(indicador__in=indicadores, avaliador=avaliador)

    # Agrupa os indicadores por dimensão
    indicadores_por_dimensao = {}
    for indicador in indicadores:
        if indicador.dimensao not in indicadores_por_dimensao:
            indicadores_por_dimensao[indicador.dimensao] = []
        indicadores_por_dimensao[indicador.dimensao].append(indicador)

    context = {
        'avaliacao': avaliacao,
        'avaliador': avaliador,
        'indicadores_por_dimensao': indicadores_por_dimensao,
        'arquivos': arquivos,
    }
    return render(request, 'avaliacoes/distribuidor_detalhes_avaliacao_arquivos.html', context)

#indicadores
@login_required
def criar_indicador(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.user != avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para criar indicadores nesta avaliação.')
        return redirect('avaliacoes:home')

    if request.method == 'POST':
        # Cria um novo indicador com os dados do formulário
        nome = request.POST['nome']
        dimensao = request.POST['dimensao']
        Indicador.objects.create(nome=nome, dimensao=dimensao, avaliacao=avaliacao)

    # Obtém os indicadores por dimensão
    indicadores = Indicador.objects.filter(avaliacao=avaliacao)
    indicadores_por_dimensao = {}
    for indicador in indicadores:
        if indicador.dimensao not in indicadores_por_dimensao:
            indicadores_por_dimensao[indicador.dimensao] = []
        indicadores_por_dimensao[indicador.dimensao].append(indicador)

    return render(request, 'avaliacoes/criar_indicador.html', {
        'avaliacao': avaliacao,
        'indicadores_por_dimensao': indicadores_por_dimensao,
    })


@login_required
def excluir_indicador(request, indicador_id):
    indicador = get_object_or_404(Indicador, id=indicador_id)
    if request.user != indicador.avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para excluir este indicador.')
        return redirect('avaliacoes:home')
    if request.method == 'POST':
        # Excluir arquivos relacionados
        for arquivo in indicador.arquivos.all():
            arquivo.delete()
        # Excluir indicador
        indicador.delete()
        messages.success(request, 'Indicador excluído com sucesso!')
        return redirect('avaliacoes:detalhes_avaliacao', indicador.avaliacao.id)
    return render(request, 'avaliacoes/excluir_indicador.html', {'indicador': indicador})


@login_required
def exibir_criar_indicador(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.user != avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para criar indicadores nesta avaliação.')
        return redirect('avaliacoes:home')
    return render(request, 'avaliacoes/criar_indicador.html', {'avaliacao': avaliacao})


@login_required
def copiar_indicadores(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.user != avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para copiar os indicadores desta avaliação.')
        return redirect('avaliacoes:home')
    if request.method == 'POST':
        avaliacao_id = request.POST.get('avaliacao_id')
        avaliacao_a_copiar = get_object_or_404(Avaliacao, id=avaliacao_id, distribuidor=request.user)
        indicadores = Indicador.objects.filter(avaliacao=avaliacao_a_copiar)
        for indicador in indicadores:
            Indicador.objects.create(nome=indicador.nome, dimensao=indicador.dimensao, avaliacao=avaliacao)
        messages.success(request, 'Indicadores copiados com sucesso!')
    return redirect('avaliacoes:detalhes_avaliacao', avaliacao.id)

@login_required
def editar_indicador(request, indicador_id):
    indicador = get_object_or_404(Indicador, id=indicador_id)
    if request.user != indicador.avaliacao.distribuidor:
        messages.error(request, 'Você não tem permissão para editar este indicador.')
        return redirect('avaliacoes:home')
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            indicador.nome = nome
            indicador.save()
            messages.success(request, 'Indicador atualizado com sucesso!')
    return redirect('avaliacoes:detalhes_avaliacao', indicador.avaliacao.id)

#arquivos
@login_required
def baixar_arquivo_distribuidor(request, arquivo_id):
    arquivo = get_object_or_404(ArquivoIndicador, id=arquivo_id)
    capa = CapaAvaliacao.objects.filter(avaliacao=arquivo.indicador.avaliacao, avaliador=arquivo.avaliador).first()
    if capa:
        merger = PdfFileMerger()
        merger.append(capa.capa.path)
        merger.append(arquivo.arquivo.path)
        response = FileResponse(merger, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={arquivo.arquivo.name}'
        return response
    else:
        response = FileResponse(arquivo.arquivo, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={arquivo.arquivo.name}'
        return response

@login_required
def enviar_capa(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    if request.method == 'POST':
        capa = request.FILES['capa']
        CapaAvaliacao.objects.create(capa=capa, avaliacao=avaliacao, avaliador=request.user)
        return redirect('avaliacoes:avaliador_detalhes_avaliacao', avaliacao_id)
    return render(request, 'avaliacoes/avaliador_detalhes_avaliacao.html')

@login_required
def substituir_capa(request, capa_id):
    capa = CapaAvaliacao.objects.get(id=capa_id)
    if request.method == 'POST':
        capa.capa.delete(save=False)
        capa.capa = request.FILES['capa']
        capa.save()
        return redirect('avaliacoes:avaliador_detalhes_avaliacao', avaliacao_id=capa.avaliacao_id)
    return render(request, 'avaliacoes/avaliador_detalhes_avaliacao.html')


@login_required
def apagar_capa(request, capa_id):
    capa = CapaAvaliacao.objects.get(id=capa_id)
    avaliacao_id = capa.avaliacao_id
    capa.delete()
    return redirect('avaliacoes:avaliador_detalhes_avaliacao', avaliacao_id=avaliacao_id)

@login_required
def baixar_capa(request, capa_id):
    capa = CapaAvaliacao.objects.get(id=capa_id)
    response = FileResponse(capa.capa, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={capa.capa.name}'
    return response


@login_required
def enviar_arquivo(request, indicador_id):
    indicador = get_object_or_404(Indicador, id=indicador_id)
    if request.method == 'POST':
        arquivo = request.FILES['arquivo']
        ArquivoIndicador.objects.create(arquivo=arquivo, indicador=indicador, avaliador=request.user)
        return redirect('avaliacoes:avaliador_detalhes_avaliacao', indicador.avaliacao.id)
    return render(request, 'avaliacoes/avaliador_detalhes_avaliacao.html')

@login_required
def substituir_arquivo(request, arquivo_id):
    arquivo = ArquivoIndicador.objects.get(id=arquivo_id)
    if request.method == 'POST':
        arquivo.arquivo.delete(save=False)
        arquivo.arquivo = request.FILES['arquivo']
        arquivo.save()
    return redirect('avaliacoes:avaliador_detalhes_avaliacao', avaliacao_id=arquivo.indicador.avaliacao_id)


@login_required
def apagar_arquivo(request, arquivo_id):
    arquivo = ArquivoIndicador.objects.get(id=arquivo_id)
    avaliacao_id = arquivo.indicador.avaliacao_id
    arquivo.delete()
    return redirect('avaliacoes:avaliador_detalhes_avaliacao', avaliacao_id=avaliacao_id)

@login_required
def baixar_arquivo(request, arquivo_id):
    arquivo = ArquivoIndicador.objects.get(id=arquivo_id)
    response = FileResponse(arquivo.arquivo, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={arquivo.arquivo.name}'
    return response

