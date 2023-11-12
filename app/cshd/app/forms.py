from django import forms


class PlaceholdersForm(forms.Form):
    def __init__(self, placeholders, *args, **kwargs):
        super(PlaceholdersForm, self).__init__(*args, **kwargs)
        placeholder: str = ""
        value: str = ""

        for placeholder, value in placeholders.items():
            self.fields[placeholder] = forms.CharField(
                required=False,
                initial=value,
                widget=forms.TextInput(
                    attrs={"class": "nhsuk-input nhsuk-input--width-30"}
                ),
            )
