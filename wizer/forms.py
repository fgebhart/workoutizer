from django import forms

from wizer.models import Sport, Activity, Settings, Lap


class AddSportsForm(forms.ModelForm):
    class Meta:
        model = Sport
        exclude = ('created', 'modified')


class AddActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        exclude = ('trace_file', 'created', 'modified')

    def __init__(self, *args, **kwargs):
        super(AddActivityForm, self).__init__(*args, **kwargs)
        self.fields['sport'] = forms.ModelChoiceField(queryset=Sport.objects.all().exclude(name='unknown'))


class EditActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        exclude = ('trace_file', 'created', 'modified')


class EditSettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = ('number_of_days', 'created', 'modified')
