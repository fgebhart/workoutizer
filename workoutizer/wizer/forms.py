from django.forms import ModelForm, DateInput

from .models import Sport, Activity


class AddSportsForm(ModelForm):
    class Meta:
        model = Sport
        fields = 'name', 'icon', 'color',


class AddActivityForm(ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'
        # widgets = {'date': DateInput(attrs={'class': 'datepicker'})}
