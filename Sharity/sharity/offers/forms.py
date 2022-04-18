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


class OfferSearchForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = [
            'title',
            'location',
            'start_date',
            'duration',
            'tags',
            'type'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'id': 'search-title',
            'class': 'search-form-title',
            'placeholder': 'Seach by offer title'
        })
        self.fields['location'].widget = forms.TextInput(attrs={
            'id': 'search-location',
            'class': 'search-form-location',
            'placeholder': 'Search by offer location'
        })
        self.fields['start_date'].widget = forms.widgets.DateTimeInput(attrs={
            'id': 'search-start_date',
            'class': 'search-form-start_date',
            'type': 'datetime-local',
        })
        self.fields['duration'].widget.attrs.update({
            'id': 'search-duration',
            'class': 'search-form-duration',
            'placeholder': 'Seach by offer duration'
        })
        self.fields['tags'].widget = forms.TextInput(attrs={
            'id': 'search-tags',
            'class': 'search-form-tags',
            'placeholder': 'Seach by offer tag'
        })
        self.fields['type'].widget.attrs.update({
            'id': 'search-type',
            'class': 'search-form-type',
        })
        self.fields['type'].initial = 1

        for key in self.fields.keys():
            self.fields[key].required = False