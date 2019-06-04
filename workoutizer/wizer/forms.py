from django import forms

from .models import Sport, Activity


class AddSportsForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = 'name', 'icon', 'color',


class AddActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'
