from django import forms

from .models import Sport, Activity, Settings


class AddSportsForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = '__all__'


class AddActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        exclude = ('trace_file',)

    def __init__(self, *args, **kwargs):
        super(AddActivityForm, self).__init__(*args, **kwargs)
        self.fields['sport'] = forms.ModelChoiceField(queryset=Sport.objects.all())


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'
