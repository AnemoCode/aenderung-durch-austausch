from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import ProfileForm, RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect('blog:index')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """Profile page where users view and edit their account details.

    Two independent sections post back to this view, distinguished by a
    hidden ``form_type`` field: ``profile`` (name/email) and ``password``.
    """
    profile_form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'profile':
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, _('Deine Angaben wurden gespeichert.'))
                return redirect('accounts:profile')
        elif form_type == 'password':
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Dein Passwort wurde geändert.'))
                return redirect('accounts:profile')

    return render(
        request,
        'accounts/profile.html',
        {'profile_form': profile_form, 'password_form': password_form},
    )
