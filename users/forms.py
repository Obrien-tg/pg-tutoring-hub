import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .models import CustomUser


class CustomUserRegistrationForm(UserCreationForm):
    """Enhanced registration form with user type selection and validation"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter your email address"}
        ),
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+1234567890"}
        ),
        help_text="Enter phone number in international format",
    )
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPES,
        initial="student",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    grade_level = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "e.g., Grade 8, High School"}
        ),
        help_text="Required for students only",
    )
    parent_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "parent@example.com"}
        ),
        help_text="Required for students only",
    )

    # Terms and conditions
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="I accept the Terms and Conditions and Privacy Policy",
    )

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
            "password1",
            "password2",
            "user_type",
            "phone_number",
            "grade_level",
            "parent_email",
            "terms_accepted",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes and enhance widgets
        for field_name, field in self.fields.items():
            if field_name not in ["terms_accepted"]:
                if "class" not in field.widget.attrs:
                    field.widget.attrs["class"] = "form-control"

        # Enhance password fields
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter a strong password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Confirm your password"}
        )

        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Choose a unique username"}
        )

    def clean_email(self):
        """Validate email format and uniqueness"""
        email = self.cleaned_data.get("email")
        if email:
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Enter a valid email address.")

            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "An account with this email already exists."
                )
        return email

    def clean_username(self):
        """Validate username format"""
        username = self.cleaned_data.get("username")
        if username:
            # Check username format (alphanumeric and underscores only)
            if not re.match(r"^[a-zA-Z0-9_]+$", username):
                raise forms.ValidationError(
                    "Username can only contain letters, numbers, and underscores."
                )

            # Check minimum length
            if len(username) < 3:
                raise forms.ValidationError(
                    "Username must be at least 3 characters long."
                )

        return username

    def clean_phone_number(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get("phone_number")
        if phone:
            # Remove all non-digit characters for validation
            digits_only = re.sub(r"\D", "", phone)
            if len(digits_only) < 10 or len(digits_only) > 15:
                raise forms.ValidationError(
                    "Phone number must be between 10-15 digits."
                )
        return phone

    def clean_password1(self):
        """Enhanced password validation"""
        password = self.cleaned_data.get("password1")
        if password:
            # Check minimum length
            if len(password) < 8:
                raise forms.ValidationError(
                    "Password must be at least 8 characters long."
                )

            # Check for at least one letter and one number
            if not re.search(r"[A-Za-z]", password):
                raise forms.ValidationError(
                    "Password must contain at least one letter."
                )

            if not re.search(r"\d", password):
                raise forms.ValidationError(
                    "Password must contain at least one number."
                )

        return password

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        grade_level = cleaned_data.get("grade_level")
        parent_email = cleaned_data.get("parent_email")

        # Validation for student fields
        if user_type == "student":
            if not grade_level:
                self.add_error("grade_level", "Grade level is required for students.")
            if not parent_email:
                self.add_error("parent_email", "Parent email is required for students.")
            elif parent_email:
                try:
                    validate_email(parent_email)
                except ValidationError:
                    self.add_error(
                        "parent_email", "Enter a valid parent email address."
                    )

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """Enhanced form for updating user profile"""

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "profile_picture",
            "grade_level",
            "parent_email",
            "emergency_contact_name",
            "emergency_contact_phone",
        )
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "profile_picture": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != "profile_picture":
                field.widget.attrs["class"] = "form-control"

        # Add placeholders
        self.fields["first_name"].widget.attrs["placeholder"] = "Enter your first name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter your last name"
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email"
        self.fields["phone_number"].widget.attrs["placeholder"] = "+1234567890"
        self.fields["grade_level"].widget.attrs["placeholder"] = "e.g., Grade 8"
        self.fields["parent_email"].widget.attrs["placeholder"] = "parent@example.com"
        self.fields["emergency_contact_name"].widget.attrs[
            "placeholder"
        ] = "Emergency contact name"
        self.fields["emergency_contact_phone"].widget.attrs[
            "placeholder"
        ] = "Emergency contact phone"

        # Make fields conditional based on user type
        if hasattr(self, "instance") and self.instance:
            if not self.instance.is_student:
                # Hide student-specific fields for non-students
                self.fields["grade_level"].widget = forms.HiddenInput()
                self.fields["parent_email"].widget = forms.HiddenInput()

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get("email")
        if email and self.instance:
            # Check if email exists for other users
            existing_users = CustomUser.objects.filter(email=email).exclude(
                id=self.instance.id
            )
            if existing_users.exists():
                raise forms.ValidationError(
                    "An account with this email already exists."
                )
        return email

    def clean_profile_picture(self):
        """Validate profile picture"""
        picture = self.cleaned_data.get("profile_picture")
        if picture:
            # Check file size (5MB limit)
            if picture.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 5MB )")

            # Check file type
            if not picture.content_type.startswith("image/"):
                raise forms.ValidationError("File must be an image.")

        return picture
