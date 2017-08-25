from authtools.forms import AuthenticationForm
from django import forms


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'aria-required': 'true'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'aria-required': 'true' }))
