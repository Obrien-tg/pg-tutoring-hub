from django.shortcuts import render


def home(request):
    """Home page view for PG Tutoring marketing site"""
    context = {
        "teacher_name": "Patience Gwanyanya",
        "business_name": "PG Tutoring",
        "tagline": "Bringing Education to Your Phone",
    }
    return render(request, "core/home.html", context)


def spa_view(request):
    return render(request, "spa/index.html")
