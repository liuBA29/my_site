# main_app/views.py

from django.shortcuts import render, redirect, get_object_or_404

from .models import *


def main_page(request):
    project = Project.objects.all().values('title', 'description')
    return render(request, 'main_app/index.html')


def useful_soft(request):
    soft = UsefulSoftware.objects.all()
    context = {'soft': soft}

    return render(request, 'main_app/useful_soft.html', context)

def useful_soft_detail(request, slug):
    soft = get_object_or_404(UsefulSoftware, slug=slug)
    context = {'soft': soft}

    return render(request, 'main_app/useful_soft_detail.html', context)

def my_projects(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'main_app/my_projects.html', context)

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)

    context = {'project':project}
    return render(request, 'main_app/project_detail.html', context)



def contact(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/contact.html')

