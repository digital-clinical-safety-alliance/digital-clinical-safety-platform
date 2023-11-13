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

    # TODO need to check no invalid values entered eg '{}'


class MDEditForm(forms.Form):
    text_md = forms.CharField(
        label="",
        required=False,
        widget=forms.Textarea(
            attrs={
                "style": "width:100%; height:1500px;",
                "class": "nhsuk-textarea",
                "onkeyup": "update_web_view( )",
            }
        ),
    )
