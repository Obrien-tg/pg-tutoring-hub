from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserRegistrationForm(UserCreationForm):
    """Enhanced registration form with user type selection"""
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPES, initial='student')
    grade_level = forms.CharField(max_length=20, required=False, help_text="For students only")
    parent_email = forms.EmailField(required=False, help_text="For students only")
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 
                 'phone_number', 'grade_level', 'parent_email')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in ['password1', 'password2']:
                field.widget.attrs['class'] += ' form-control'
                
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        grade_level = cleaned_data.get('grade_level')
        parent_email = cleaned_data.get('parent_email')
        
        # Validation for student fields
        if user_type == 'student':
            if not grade_level:
                raise forms.ValidationError("Grade level is required for students.")
            if not parent_email:
                raise forms.ValidationError("Parent email is required for students.")
                
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 
                 'date_of_birth', 'profile_picture', 'grade_level', 'parent_email')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'