from django import forms
from .models import Url


'''class UrlForm(forms.ModelForm):
    class Meta:
        model = Url
        fields = [
            'originalurl',
            'tinyurl',
            'description'
        ]
'''
class SuggestUrl(forms.Form):
    o_url = forms.CharField(max_length=500)
    suggest_url = forms.CharField(max_length=10,required=False)
