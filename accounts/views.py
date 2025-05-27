from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .forms import StudentRegistrationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def home(request):
    return render(request, 'accounts/home.html')

def logout_view(request):
    if request.method == 'POST':
        # User confirmed logout, so log them out
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('login')
    else:
        # Display the logout confirmation page
        return render(request, 'accounts/logout.html')
