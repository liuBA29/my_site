from django.shortcuts import render

def main_page(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/index.html')


def useful_soft(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/useful_soft.html')

def my_projects(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/my_projects.html')


def contact(request):
    #clients = Client.objects.all().values('id', 'name', 'is_active')
    return render(request, 'main_app/contact.html')