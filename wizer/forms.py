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
        self.fields['sport'] = forms.ModelChoiceField(queryset=Sport.objects.all().exclude(name='unknown'))


class EditActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        exclude = ('trace_file',)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = ('number_of_days',)
