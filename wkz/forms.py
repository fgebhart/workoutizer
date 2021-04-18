from django import forms

from wkz.models import Sport, Activity, Settings


DATETIMEPICKER_FORMAT = "%m/%d/%Y %I:%M %p"


def set_field_attributes(visible_fields):
    for visible in visible_fields:
        if visible.name == "date":  # because it would overwrite the required 'datetimepicker' class
            continue
        else:
            visible.field.widget.attrs["class"] = "form-control"


class AddSportsForm(forms.ModelForm):
    class Meta:
        model = Sport
        exclude = ("created", "modified")

    def __init__(self, *args, **kwargs):
        super(AddSportsForm, self).__init__(*args, **kwargs)
        set_field_attributes(self.visible_fields())


class AddActivityForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=[DATETIMEPICKER_FORMAT],
        widget=forms.DateTimeInput(attrs={"class": "form-control datetimepicker"}),
    )

    class Meta:
        model = Activity
        exclude = ("trace_file", "created", "modified", "is_demo_activity", "evaluates_for_awards")

    def __init__(self, *args, **kwargs):
        super(AddActivityForm, self).__init__(*args, **kwargs)
        self.fields["sport"] = forms.ModelChoiceField(queryset=Sport.objects.all().exclude(name="unknown"))
        set_field_attributes(self.visible_fields())


class EditActivityForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=[DATETIMEPICKER_FORMAT],
        widget=forms.DateTimeInput(attrs={"class": "form-control datetimepicker"}),
    )

    class Meta:
        model = Activity
        exclude = ("trace_file", "created", "modified", "is_demo_activity")

    def __init__(self, *args, **kwargs):
        super(EditActivityForm, self).__init__(*args, **kwargs)
        self.fields["sport"] = forms.ModelChoiceField(queryset=Sport.objects.all().exclude(name="unknown"))
        set_field_attributes(self.visible_fields())


class EditSettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        exclude = ("number_of_days", "created", "modified")

    def __init__(self, *args, **kwargs):
        super(EditSettingsForm, self).__init__(*args, **kwargs)
        set_field_attributes(self.visible_fields())
