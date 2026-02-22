from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django import forms

User = get_user_model()


class EmailLoginForm(AuthenticationForm):
    """Replaces the username CharField with an email field."""

    username = forms.EmailField(
        label='E-Mail-Adresse',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Passwort',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    password2 = forms.CharField(
        label='Passwort bestätigen',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ['name', 'email']

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Die Passwörter stimmen nicht überein.')
        return p2

    def _post_clean(self):
        """Run Django's password validators against the not-yet-saved User instance."""
        super()._post_clean()
        password = self.cleaned_data.get('password1')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error('password1', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
