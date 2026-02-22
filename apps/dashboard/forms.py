from django import forms
from django.contrib.auth import get_user_model

from .models import GroupProject, GroupMembership, Project, ProjectGroup

User = get_user_model()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'git_url']


class ProjectGroupForm(forms.ModelForm):
    class Meta:
        model = ProjectGroup
        fields = ['name']


class AddMemberForm(forms.Form):
    """Looks up a user by email address and validates they're not already a member."""

    email = forms.EmailField(label='E-Mail-Adresse')

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('Kein Benutzer mit dieser E-Mail-Adresse gefunden.')
        if self.group.memberships.filter(user=user).exists():
            raise forms.ValidationError('Dieser Benutzer ist bereits Mitglied dieser Gruppe.')
        return user  # Return the resolved User object for the view to use directly


class AddProjectToGroupForm(forms.Form):
    """Presents only projects owned by the user that aren't yet in the group."""

    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        empty_label='Projekt auswählen…',
        label='Projekt',
    )

    def __init__(self, group, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        already_added = group.projects.values_list('pk', flat=True)
        self.fields['project'].queryset = (
            Project.objects.filter(owner=user).exclude(pk__in=already_added)
        )
