from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegisterForm
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'main/base.html')

def login(request):
    return render(request, 'auth/login.html')

def logout(request):
    pass
# def register(request):
#     return render(request, 'auth/register.html')

def register(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = RegisterForm()
    return render(response, "auth/register.html", {"form": form})
