import json
from django import forms
from .models import Offer


class OfferCreateForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    description = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': '3',
    }))
    location = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'location',
        'style': 'padding: 0.375rem 1.75rem 0.375rem 0.75rem;',
    }))
    start_date = forms.DateTimeField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'datetime-local',
    }))
    amendment_deadline = forms.DateTimeField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': "datetime-local"
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
    claims = forms.CharField(widget=forms.HiddenInput(attrs={
        'value': '[]',
    }))
    type = forms.ChoiceField(choices=Offer.Type.choices, widget=forms.Select(attrs={
        'class': 'form-select',
    }))

    class Meta:
        model = Offer
        fields = (
            'title',
            'description',
            'location',
            'start_date',
            'amendment_deadline',
            'duration',
            'participant_limit',
            'photo',
            'tags',
            'type',
            'claims',
        )

    @property
    def tag_ids(self):
        tags_json = json.loads(self.cleaned_data['tags'].replace("\\'", '"'))
        return tuple([tag['id'] for tag in tags_json])


class OfferSearchForm(forms.ModelForm):
    owner = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'id': 'search-owner',
        'class': 'search-form-owner',
        'placeholder': 'Search by owner name'
    }))
    distance = forms.IntegerField()
    keyword = forms.CharField(max_length=250, required=False)

    class Meta:
        model = Offer
        fields = [
            'location',
            'start_date',
            'duration',
            'tags',
            'type',
        ]

    field_order = ['keyword', 'start_date', 'duration', 'tags', 'type', 'owner', 'location', 'distance']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keyword'].widget.attrs.update({
            'id': 'search-keyword',
            'class': 'search-form-keyword',
            'placeholder': 'Search by keyword'
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
            'placeholder': 'Search by offer duration'
        })
        self.fields['tags'].widget = forms.TextInput(attrs={
            'id': 'search-tags',
            'class': 'search-form-tags',
            'placeholder': 'Search by offer tag'
        })
        self.fields['type'].widget.attrs.update({
            'id': 'search-type',
            'class': 'search-form-type',
        })

        new_choices = list(self.fields['type'].choices)
        new_choices.remove(('', '---------'))
        new_choices.insert(0, ('', 'All'))
        self.fields['type'].choices = new_choices
        self.fields['type'].initial = ''

        self.fields['distance'].widget.attrs.update({
            'id': 'search-distance',
            'class': 'search-form-distance',
            'placeholder': 'Search by distance'
        })

        for key in self.fields.keys():
            self.fields[key].required = False

    def clean(self):
        if (self.data.get('location-json') != '' and self.data.get('map-json') != '') or (
                self.data.get('location') != '' and self.data.get('map-json') != ''):
            raise forms.ValidationError('Only one location can be inputted.')

        cleaned_data = self.cleaned_data
        if self.data.get('location-json') != '':
            cleaned_data['location-json'] = self.data.get('location-json')
        elif self.data.get('map-json') != '':
            cleaned_data['location-json'] = self.data.get('map-json')
        else:
            cleaned_data['location-json'] = ''

        return cleaned_data


class OfferForm(forms.ModelForm):
    # Information is shown for all fields other than 'providerID'
    class Meta:
        model = Offer
        fields = '__all__'
