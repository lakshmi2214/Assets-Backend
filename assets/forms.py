from django import forms
from .models import Booking, Location


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'asset',
            'start_datetime',
            'end_datetime',
            'purpose',
            'contact_name',
            'contact_email',
            'contact_address',
            'contact_mobile',
            'contact_location',
        ]
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'asset': forms.HiddenInput(),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_datetime')
        end = cleaned.get('end_datetime')
        if start and end and start >= end:
            raise forms.ValidationError('End must be after start.')
        return cleaned
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes to widgets for nicer visuals
        for name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')
            if 'form-control' not in css:
                field.widget.attrs['class'] = (css + ' form-control').strip()
