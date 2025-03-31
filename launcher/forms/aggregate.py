from django import forms
from django.forms import ValidationError
from django.utils.translation import gettext as _

from launcher.cache.albums import retrieve_user_albums


class AggregateForm(forms.Form):
    album = forms.ChoiceField()
    series_description_filter = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control my-2', 'placeholder': 'ex. "my_algo:0.1.0"'},
        )
    )
    output_format = forms.ChoiceField(
        choices=[('json', 'json'), ('csv', 'csv')],
        widget=forms.Select(attrs={'class': 'form-select my-2'})
    )

    def __init__(self, access_token: str, user_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['album'].widget = forms.Select(
            choices=[(album.id_, album.label) for album in retrieve_user_albums(access_token, user_id)],
            attrs={'class': 'form-select my-2'},
        )

    def clean_series_description_filter(self):
        """Validate field."""
        series_description_filter = self.cleaned_data['series_description_filter']
        series_description_filter = series_description_filter.split(' - ')[0]

        if ':' not in series_description_filter:
            raise ValidationError(f'"{series_description_filter}" ' + _('does not seems to be a valid algorithm name (e.g. my_algo:0.1.0).'))

        return series_description_filter
