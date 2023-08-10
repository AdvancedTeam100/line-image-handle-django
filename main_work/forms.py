from django import forms
from .models import Upload_image
#DataFlair #File_Upload
class Profile_Form(forms.ModelForm):
    class Meta:
        model = Upload_image
        fields = [
        'display_image'
        ]
    labels = {
            'display audio': 'オーディオ選択'
        }