from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth import logout
from avaliacoes.views import listar_avaliacoes
from avaliacoes.models import Avaliacao


def logout_view(request):
    logout(request)
    return redirect('contas:login')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f'Usuário salvo: {user.username}, tipo: {user.user_type}')
            login(request, user)
            print(f'Usuário autenticado: {request.user.is_authenticated}') # Imprime se o usuário está autenticado
            if user.user_type == 'distribuidor':
                return redirect('avaliacoes:home')
            else:
                return redirect('avaliacoes:home')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, 'contas/cadastro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        print(request.POST)  # Imprime o valor de request.POST
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(user) # Imprime o valor de user
        if user is not None:
            login(request, user)
            if user.user_type == 'distribuidor':
                return redirect('avaliacoes:home')
            else:
                return redirect('avaliacoes:home')
        else:
            messages.error(request, 'Nome de usuário ou senha incorretos')
    return render(request, 'contas/login.html')

def editar_perfil(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('detalhes_usuario')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'contas/editar_perfil.html', {'form': form})


def detalhes_usuario(request, pk=None):
    if pk:
        usuario = CustomUser.objects.get(pk=pk)
    else:
        usuario = request.user

    if request.user.user_type in ['distribuidor', 'avaliador']:
        if request.user.user_type == 'distribuidor':
            avaliacoes = Avaliacao.objects.filter(distribuidor=request.user, avaliadores=usuario)
        else:
            avaliacoes = Avaliacao.objects.filter(avaliadores=request.user, distribuidor=usuario)
    else:
        avaliacoes = listar_avaliacoes(request)

    return render(request, 'contas/perfil_detalhes.html', {'usuario': usuario, 'avaliacoes': avaliacoes})