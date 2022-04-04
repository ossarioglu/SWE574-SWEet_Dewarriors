from django import forms
from .models import Offer


class OfferCreateForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    location = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'location',
        'style': 'padding: 0.375rem 1.75rem 0.375rem 0.75rem;',
    }))
    start_date = forms.DateTimeField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'datepicker',
    }))
    amendment_deadline = forms.DateTimeField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'datepicker',
    }))
    duration = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    participant_limit = forms.IntegerField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    photo = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'input-file',
        'id': 'formFile',
    }))
    tags = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'tags',
        'style': 'padding: 0.375rem 1.75rem 0.375rem 0.75rem;',
    }))
    type = forms.ChoiceField(choices=Offer.Type.choices, widget=forms.Select(attrs={
        'class': 'form-control',
    }))

    class Meta:
        model = Offer
        fields = (
            'title',
            'location',
            'start_date',
            'amendment_deadline',
            'duration',
            'participant_limit',
            'photo',
            'tags',
            'type',
        )
