from django.shortcuts import render, get_object_or_404
from .models import Material, Assignment, StudentProgress


def materials_list(request):
    """List all available materials"""
    materials = Material.objects.filter(is_active=True)
    return render(request, 'hub/materials_list.html', {'materials': materials})


def material_detail(request, pk):
    """Show details of a specific material"""
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'hub/material_detail.html', {'material': material})


def assignments_list(request):
    """List student assignments"""
    # If logged in, show assigned assignments; otherwise show all
    if request.user.is_authenticated and request.user.is_student:
        assignments = Assignment.objects.filter(assigned_to=request.user)
    else:
        assignments = Assignment.objects.all()
    return render(request, 'hub/assignments_list.html', {'assignments': assignments})


def progress_view(request):
    """Show student progress"""
    if request.user.is_authenticated and request.user.is_student:
        progress_list = StudentProgress.objects.filter(student=request.user)
    else:
        progress_list = StudentProgress.objects.none()
    return render(request, 'hub/progress.html', {'progress_list': progress_list})
