from django import forms
from myapp.models import User


class MyAccountForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, label='*First Name', required=True)
    last_name = forms.CharField(max_length=50, label='*Last Name', required=True)
    email = forms.EmailField(label='*Email', required=True)
    balance = forms.DecimalField(disabled=True)

    class Meta:
        model = User
        fields = '__all__'
