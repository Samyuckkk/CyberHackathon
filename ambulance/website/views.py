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
from django.utils import timezone
from datetime import timedelta

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

    vitals_data = []

    from .models import AmbulanceStatus  # import inside function to avoid circular import

    for user in ambulance_users:
        vitals = Vitals.objects.filter(user=user).first()
        status_entry = AmbulanceStatus.objects.filter(user=user).first()
        is_active = status_entry.is_active if status_entry else False

        # Mark inactive if no vitals update for >10 seconds
        if vitals and (timezone.now() - vitals.last_updated) > timedelta(seconds=10):
            is_active = False

        if is_active and vitals:
            vitals_data.append({
                "username": user.username,  # 👈 include for JS matching
                "name": user.first_name,
                "ecg": vitals.ecg,
                "spo2": vitals.spo2,
                "nibp": vitals.nibp,
                "rr": vitals.rr,
                "temp": vitals.temp,
                "status": "Active" if vitals.status != "Critical" else "Critical"
            })
        else:
            vitals_data.append({
                "username": user.username,  # 👈 include for JS matching
                "name": user.first_name,
                "ecg": "--",
                "spo2": "--",
                "nibp": "--",
                "rr": "--",
                "temp": "--",
                "status": "Inactive"
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
        data["username"] = request.user.username
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

# def get_all_vitals(request):
#     try:
#         # Get all users in the "ambulance" group
#         ambulance_group = Group.objects.get(name='ambulance')
#         ambulance_users = ambulance_group.user_set.all()
#     except Group.DoesNotExist:
#         return JsonResponse([], safe=False)

#     data = []

#     for user in ambulance_users:
#         try:
#             # Get the latest vitals for that ambulance user
#             vitals = Vitals.objects.filter(user=user).latest('last_updated')

#             # Check if the data is recent (last 10 seconds)
#             recent = (timezone.now() - vitals.last_updated).seconds <= 10

#             data.append({
#                 'name': user.first_name or user.username,
#                 'ecg': vitals.ecg if recent else "--",
#                 'spo2': vitals.spo2 if recent else "--",
#                 'nibp': vitals.nibp if recent else "--",
#                 'rr': vitals.rr if recent else "--",
#                 'temp': vitals.temp if recent else "--",
#                 'status': vitals.status if recent else "Inactive",
#             })
#         except Vitals.DoesNotExist:
#             # No data found for this ambulance
#             data.append({
#                 'name': user.first_name or user.username,
#                 'ecg': "--",
#                 'spo2': "--",
#                 'nibp': "--",
#                 'rr': "--",
#                 'temp': "--",
#                 'status': "Inactive",
#             })

#     return JsonResponse(data, safe=False)