from django import forms
from bootstrap_datepicker_plus import DateTimePickerInput

from wizer.models import Sport, Activity, Settings


class AddSportsForm(forms.ModelForm):
    class Meta:
        model = Sport
        exclude = ("created", "modified")


class AddActivityForm(forms.ModelForm):
    date = forms.DateTimeField(widget=DateTimePickerInput())

    class Meta:
        model = Activity
        exclude = ("trace_file", "created", "modified")

    def __init__(self, *args, **kwargs):
        super(AddActivityForm, self).__init__(*args, **kwargs)
        self.fields["sport"] = forms.ModelChoiceField(queryset=Sport.objects.all().exclude(name="unknown"))


class EditActivityForm(forms.ModelForm):
    date = forms.DateTimeField(widget=DateTimePickerInput())

    class Meta:
        model = Activity
        exclude = ("trace_file", "created", "modified", "is_demo_activity")


class EditSettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = ("number_of_days", "created", "modified")
