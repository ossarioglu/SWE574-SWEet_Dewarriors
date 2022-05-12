from django import forms
from .models import UserMessage
from member.models import Profile

class UserMessageModelForm(forms.ModelForm):
    to = forms.CharField(max_length=250)
    class Meta:
        model = UserMessage
        fields = ['subject', 'body']

    field_order = ['to', 'subject', 'body']

    def clean_to(self):
        to_list = [i.strip() for i in self.cleaned_data.get('to').split(';') if i.strip() != '']
        if len(to_list) == 0:
            raise forms.ValidationError('You need to enter a username to send a message!')
            
        try:
            profiles = [Profile.objects.get(user__username=t) for t in to_list]
        except Profile.DoesNotExist:
            raise forms.ValidationError('One or more usernames are not registered!')
        return profiles

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if subject == '':
            subject = 'No Title'
        return subject

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 2:
            raise forms.ValidationError('This is not long enough.')
        return body

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in self.fields.keys():
            self.fields[key].widget.attrs.update({
                'class': 'form-control',
                'id': 'id-form-' + key
            })
