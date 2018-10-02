
from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class URLForm(forms.Form):  # Note that it is not inheriting from forms.ModelForm
    url = forms.CharField(max_length=100, help_text="Enter a valid url i.e., gunosy.com/articles/RSp3z")
    
    def clean_url(self):
        """ cleans the form url data """
        data = self.cleaned_data['url']
        
        gunosy = 'gunosy.com'
        needed_part = 'articles'
        parts = data.split('/')
        
        try:
            index = parts.index(needed_part)
            article_id = parts[index + 1]
            arr = ['https:/', gunosy, needed_part, article_id]
            new_data = '/'.join(arr)
            return new_data
        except Exception as e:
            print(e)
            raise ValidationError(_('Enter a valid link'), code='invalid')
