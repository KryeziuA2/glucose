from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from .models import Food  # Import the Food model if not already imported


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
        # You can add more fields like email, first_name, last_name etc.

class MealLogForm(forms.Form):
    food = forms.ModelMultipleChoiceField(queryset=Food.objects.all(), widget=forms.CheckboxSelectMultiple)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))