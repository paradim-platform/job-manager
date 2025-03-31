from django import forms

from manager import models
from manager.models import Runnable
from launcher.cache.albums import retrieve_user_albums


class LauncherForm(forms.Form):
    runnables = forms.ModelChoiceField(
        queryset=Runnable.objects.filter(is_active=True),
        widget=forms.Select(
            attrs={'class': 'form-select my-2'},
        ),
    )
    albums = forms.ChoiceField()
    study_date = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control my-2',
                'placeholder': 'ex. "2001-02-*"'
            },
        ),
        required=False
    )
    series_description = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control my-2',
                'placeholder': 'ex. "my_algo*"'
            },
        ),
        required=False
    )

    def __init__(self, access_token: str, user_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['albums'].widget = forms.Select(
            choices=[(album.id_, album.label) for album in retrieve_user_albums(access_token, user_id)],
            attrs={'class': 'form-select my-2'},
        )

        runnables = [(runnable.pk, str(runnable)) for runnable in models.Runnable.objects.filter(is_active=True)]
        runnables = sorted(runnables, key=lambda r: r[1])
        self.fields['runnables'].widget = forms.Select(
            choices=runnables,
            attrs={'class': 'form-select my-2'},
        )
