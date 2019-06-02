from django.forms import ModelForm

from .models import Sport, Activity


class AddSportsForm(ModelForm):
    class Meta:
        model = Sport
        fields = '__all__'


class AddActivityForm(ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'

