from django import forms
from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = [
            'title',          # Notice title
            'content',    # Full description/content
            'target_class',   # Optional: which class it targets
            'department',     # Optional: department
            'priority',       # Optional: high/low
            'expiry_date',    # Optional: expiry of notice
            'attachment',     # Optional: file attachment
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }
