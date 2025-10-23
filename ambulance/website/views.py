from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

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
    # Get all users in 'ambulance' group
    try:
        ambulance_group = Group.objects.get(name='ambulance')
        ambulance_users = ambulance_group.user_set.all()
    except Group.DoesNotExist:
        ambulance_users = []

    # Example: mock vitals for each user
    vitals_data = []
    for i, user in enumerate(ambulance_users, start=1):
        vitals_data.append({
            "name": user.first_name,
            "ecg": f"HR {70 + i*2} bpm",
            "spo2": f"{95 + i}%","nibp": f"{110 + i}/{70 + i} mmHg",
            "rr": f"{18 + i}/min",
            "temp": f"{98 + i*0.5}°F",
            "status": "Critical" if i == 1 else "Stable"
        })

    return render(request, 'hospital_dash.html', {'role': 'hospital','vitals_data': vitals_data})

@login_required
def ambulance_dash(request):

    return render(request, 'ambulance_dash.html', {'role' : 'ambulance'})