from django import forms

from launcher.cache.albums import retrieve_user_albums
from manager.models import Runnable


class AggregateForm(forms.Form):
    album = forms.ChoiceField()
    runnable = forms.ModelChoiceField(
        queryset=Runnable.objects.filter(is_active=True),
        widget=forms.Select(
            attrs={'class': 'form-select my-2'},
        ),
    )
    series_description_filter = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control my-2',
                'placeholder': 'ex. "my_algo:0.0.1 - *something*"'
            },
        ),
        required=False
    )
    output_format = forms.ChoiceField(
        choices=[('json', 'json'), ('csv', 'csv')],
        widget=forms.Select(attrs={'class': 'form-select my-2'})
    )

    def __init__(self, access_token: str, user_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        albums = [(album.id_, album.label) for album in retrieve_user_albums(access_token, user_id)]
        albums = sorted(albums, key=lambda a: a[1])
        self.fields['album'].widget = forms.Select(
            choices=albums,
            attrs={'class': 'form-select my-2'},
        )

    def clean_series_description_filter(self):
        """
        If a custom series_description_filter was used, validated it at least fit the runnable (app:version).
        If not, raise a bad form error.
        """
        series_description_filter = self.cleaned_data['series_description_filter']
        runnable = self.cleaned_data['runnable']

        app_name = runnable.app.name
        app_version = runnable.runnable.version
        if series_description_filter and not series_description_filter.startswith(f'{app_name}:{app_version}'):
            raise forms.ValidationError(f'The series_description_filter must start with "{app_name}:{app_version}"')
