from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .models import Vitals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

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
    try:
        ambulance_group = Group.objects.get(name='ambulance')
        ambulance_users = ambulance_group.user_set.all()
    except Group.DoesNotExist:
        ambulance_users = []

    # ✅ Fetch actual vitals for each ambulance user
    vitals_data = []
    for user in ambulance_users:
        vitals = Vitals.objects.filter(user=user).first()
        if vitals:
            vitals_data.append({
                "name": user.first_name,
                "ecg": vitals.ecg,
                "spo2": vitals.spo2,
                "nibp": vitals.nibp,
                "rr": vitals.rr,
                "temp": vitals.temp,
                "status": vitals.status,
            })
        else:
            # fallback in case a Vitals record doesn't exist yet
            vitals_data.append({
                "name": user.first_name,
                "ecg": "--",
                "spo2": "--",
                "nibp": "--",
                "rr": "--",
                "temp": "--",
                "status": "No Data",
            })

    return render(request, 'hospital_dash.html', {
        'role': 'hospital',
        'vitals_data': vitals_data,
    })


@login_required
def ambulance_dash(request):

    return render(request, 'ambulance_dash.html', {'role' : 'ambulance'})






@login_required
def send_vitals(request):
    """Called by ambulance dashboard to push new vitals to hospital"""
    if request.method == "POST":
        data = json.loads(request.body)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "vitals_room", {"type": "send_vitals", "data": data}
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def update_vitals(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        vitals, _ = Vitals.objects.get_or_create(user=user)

        vitals.ecg = data.get('ecg', vitals.ecg)
        vitals.spo2 = data.get('spo2', vitals.spo2)
        vitals.nibp = data.get('nibp', vitals.nibp)
        vitals.rr = data.get('rr', vitals.rr)
        vitals.temp = data.get('temp', vitals.temp)
        vitals.status = data.get('status', vitals.status)
        vitals.save()

        return JsonResponse({'message': 'Vitals updated successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_all_vitals(request):
    vitals = Vitals.objects.select_related('user').all()
    data = [
        {
            'name': v.user.username,
            'ecg': v.ecg,
            'spo2': v.spo2,
            'nibp': v.nibp,
            'rr': v.rr,
            'temp': v.temp,
            'status': v.status
        } for v in vitals
    ]
    return JsonResponse(data, safe=False)