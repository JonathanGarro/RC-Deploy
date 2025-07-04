from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, LanguageProficiency, Language, Airport
from django.forms import inlineformset_factory

class UserForm(forms.ModelForm):
    """
    Form for updating user information.
    """
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'accept_sms', 'closest_airport', 'bio')
        widgets = {
            'accept_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'closest_airport': forms.Select(attrs={'class': 'form-select airport-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LanguageProficiencyForm(forms.ModelForm):
    """
    Form for adding/updating language proficiency.
    """
    class Meta:
        model = LanguageProficiency
        fields = ('language', 'proficiency')
        widgets = {
            'language': forms.Select(attrs={'class': 'form-select'}),
            'proficiency': forms.Select(attrs={'class': 'form-select'}),
        }


# Create a formset for language proficiencies
LanguageProficiencyFormSet = inlineformset_factory(
    UserProfile,
    LanguageProficiency,
    form=LanguageProficiencyForm,
    extra=1,
    can_delete=True
)
