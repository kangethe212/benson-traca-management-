from django.shortcuts import render
from django.utils import timezone

def home(request):
    """Simple homepage"""
    context = {
        'year': timezone.now().year,
    }
    return render(request, 'listings/home.html', context)
