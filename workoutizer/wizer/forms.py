from django import forms

from .models import Sport, Activity, Settings


class AddSportsForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = 'name', 'icon', 'color',


class AddActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = '__all__'


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'
