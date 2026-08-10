from django import forms

from .models import ContactInquiry


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'company', 'service', 'budget', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': 'you@company.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': '+1 555 000 0000',
            }),
            'company': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': 'Company (optional)',
            }),
            'service': forms.Select(attrs={
                'class': 'input',
            }),
            'budget': forms.Select(attrs={
                'class': 'input',
            }),
            'message': forms.Textarea(attrs={
                'class': 'input',
                'placeholder': 'Tell me about your project, timeline, and goals...',
                'rows': 5,
            }),
        }