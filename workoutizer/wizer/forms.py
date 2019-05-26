from django import forms
from django.forms import ModelForm, Textarea

from .models import Sport


class AddSportsForm(ModelForm):
    class Meta:
        model = Sport
        fields = '__all__'

