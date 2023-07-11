from django import forms
from .models import Avaliacao, Indicador, ArquivoIndicador, CapaAvaliacao
from contas.models import CustomUser

class AvaliacaoForm(forms.ModelForm):
    avaliadores = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(user_type='avaliador'),
        widget=forms.CheckboxSelectMultiple,
        label='Avaliadores',
        required=False
    )

    class Meta:
        model = Avaliacao
        fields = ('nome', 'inscricao', 'avaliadores')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avaliadores'].label_from_instance = lambda obj: obj.name

    def clean(self):
        cleaned_data = super().clean()
        avaliadores = cleaned_data.get('avaliadores')
        if not avaliadores:
            self.add_error('avaliadores', 'Selecione pelo menos um avaliador.')

class IndicadorForm(forms.ModelForm):
    class Meta:
        model = Indicador
        fields = ('nome', 'dimensao')

class ArquivoIndicadorForm(forms.ModelForm):
    class Meta:
        model = ArquivoIndicador
        fields = ('arquivo', 'indicador', 'avaliador')

class CapaAvaliacaoForm(forms.ModelForm):
    class Meta:
        model = CapaAvaliacao
        fields = ('capa', 'avaliacao', 'avaliador')