from django import forms
from myapp.models import UserProfile
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='*User Name', required=True)
    first_name = forms.CharField(max_length=150, label='*First Name', required=True)
    last_name = forms.CharField(max_length=150, label='*Last Name', required=True)
    email = forms.EmailField(max_length=254, label='*Email', required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class UserProfileForm(forms.ModelForm):
    balance = forms.DecimalField(disabled=True)

    class Meta:
        model = UserProfile
        fields = ['balance']
