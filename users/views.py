from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import CustomUserRegistrationForm, UserProfileForm
from .models import CustomUser

class CustomLoginView(LoginView):
    """Custom login view with role-based redirects"""
    template_name = 'users/login.html'
    
    def get_success_url(self):
        return '/dashboard/'  # Use the dashboard index which will redirect appropriately

def register(request):
    """User registration view"""
    # Get role from URL parameter if provided
    initial_role = request.GET.get('role', 'student')
    
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            user_type = form.cleaned_data.get('user_type')
            
            messages.success(request, f'Welcome to PG Tutoring, {username}! Your {user_type} account has been created.')
            login(request, user)  # Auto-login after registration
            
            # Redirect based on user type
            return redirect('dashboard:index')
    else:
        # Pre-populate form with role from URL parameter
        form = CustomUserRegistrationForm(initial={'user_type': initial_role})
    
    context = {
        'form': form,
        'selected_role': initial_role,
        'role_info': {
            'student': {
                'title': 'Student Registration',
                'description': 'Join PG Tutoring to access personalized learning materials, assignments, and chat with Teacher Patience.',
                'icon': 'fas fa-graduation-cap',
                'color': 'primary'
            },
            'parent': {
                'title': 'Parent Registration', 
                'description': 'Monitor your child\'s progress, communicate with Teacher Patience, and stay involved in their learning journey.',
                'icon': 'fas fa-users',
                'color': 'success'
            },
            'teacher': {
                'title': 'Teacher Registration',
                'description': 'Manage students, create assignments, upload materials, and build your tutoring community.',
                'icon': 'fas fa-chalkboard-teacher', 
                'color': 'info'
            }
        }
    }
    
    return render(request, 'users/register.html', context)

@login_required
def profile_view(request):
    """User profile view and edit"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})

@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user type"""
    return redirect('dashboard:index')
