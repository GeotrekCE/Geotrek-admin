import floppyforms as forms
from crispy_forms.helper import FormHelper



class MapEntityForm(forms.ModelForm):
    formfield_callback = lambda f: MapEntityForm.make_tinymce_widget(f)

    pk = forms.Field(required=False, widget=forms.Field.hidden_widget)
    model = forms.Field(required=False, widget=forms.Field.hidden_widget)

    helper = FormHelper()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MapEntityForm, self).__init__(*args, **kwargs)
        # Generic behaviour
        if self.instance.pk:
            self.helper.form_action = self.instance.get_update_url()
        else:
            self.helper.form_action = self.instance.get_add_url()
        self.fields['pk'].initial = self.instance.pk
        self.fields['model'].initial = self.instance._meta.module_name
