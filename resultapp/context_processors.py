# resultapp/context_processors.py
from .models import Notice
from django.utils import timezone

def get_global_notices(request):
    """
    Always provide latest valid notices to all templates.
    """
    notices = Notice.objects.filter(
        expiry_date__gte=timezone.now()
    ) | Notice.objects.filter(expiry_date__isnull=True)

    return {
        'notices': notices.order_by('-publish_date')[:5]  # latest 5 notices
    }



def latest_notices(request):
    return {
        "latest_notices": Notice.objects.all().order_by('-created_at')[:5]
    }
