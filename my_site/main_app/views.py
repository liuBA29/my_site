from django.shortcuts import render, redirect, get_object_or_404

from .models import *


def main_page(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/index.html')


def useful_soft(request):
    context = {}
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/useful_soft.html', context)

def useful_soft_detail(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/useful_soft_detail.html')

def my_projects(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/my_projects.html')

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)

    context = {'project':project}
    return render(request, 'main_app/project_detail.html', context)



def contact(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/contact.html')