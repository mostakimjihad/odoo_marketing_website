from django import forms

from .models import ContactInquiry


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'company', 'service', 'budget', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'you@company.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '+1 555 000 0000',
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Company (optional)',
            }),
            'service': forms.Select(attrs={
                'class': 'form-input form-select',
            }),
            'budget': forms.Select(attrs={
                'class': 'form-input form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Tell me about your project, timeline, and goals...',
                'rows': 5,
            }),
        }