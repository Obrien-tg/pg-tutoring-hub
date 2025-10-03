from django import forms
from hub.models import Material, Assignment
from django.contrib.auth import get_user_model

class CreateMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ('title', 'description', 'material_type', 'subject', 'difficulty_level', 'file', 'external_link', 'grade_level', 'estimated_time')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CreateAssignmentForm(forms.ModelForm):
    assigned_to = forms.ModelMultipleChoiceField(queryset=get_user_model().objects.filter(user_type='student'), required=True, widget=forms.SelectMultiple)

    class Meta:
        model = Assignment
        fields = ('title', 'description', 'material', 'due_date', 'assigned_to')
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        assignment = super().save(commit=False)
        if commit:
            assignment.save()
            self.save_m2m()
        return assignment

class AnnouncementForm(forms.Form):
    RECIPIENT_CHOICES = (
        ('students', 'All Students'),
        ('parents', 'All Parents'),
    )
    recipient_group = forms.ChoiceField(choices=RECIPIENT_CHOICES)
    content = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
