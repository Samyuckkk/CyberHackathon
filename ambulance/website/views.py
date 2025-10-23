from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):

    if request.method == "POST":
        # username = request.POST['email']
        # password = request.POST['password']

        # user = authenticate(request, username=username, password=password)

        form = AuthenticationForm(request, data=request.POST)

        # if user is not None:
        #     login(request, user)
        #     return redirect('role_redirect')

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('role_redirect')
        else:
            messages.error(request, 'Incorrect email or password!')
    else:
        form = AuthenticationForm()

    return render(request, 'index.html', {'form': form})

@login_required
def role_redirect(request):

    user = request.user

    if user.groups.filter(name='hospital').exists():
        return redirect('hospital_dash')
    elif user.groups.filter(name='ambulance').exists():
        return redirect('ambulance_dash')

    return redirect('index')

@login_required
def hospital_dash(request):

    return render(request, 'hospital_dash.html', {'role' : 'hospital'})

@login_required
def ambulance_dash(request):

    return render(request, 'ambulance_dash.html', {'role' : 'ambulance'})