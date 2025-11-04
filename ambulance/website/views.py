from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .models import Vitals, AmbulanceStatus

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
    now = timezone.now()

    for user in ambulance_users:
        vitals = Vitals.objects.filter(user=user).order_by('-last_updated').first()
        status_entry, _ = AmbulanceStatus.objects.get_or_create(user=user)

        timeout_seconds = 10
        is_active = False

        if status_entry.last_seen:
            diff = (now - status_entry.last_seen).total_seconds()
            if diff <= timeout_seconds:
                is_active = True
            else:
                # Mark inactive
                if status_entry.is_active:
                    status_entry.is_active = False
                    status_entry.save(update_fields=['is_active'])
                print(f"[TIMEOUT] {user.username}: No update for {diff:.1f}s, marked inactive.")
        else:
            print(f"[NO STATUS] {user.username}: never seen active.")

        if is_active and vitals:
            vitals_data.append({
                "username": user.username,
                "name": user.first_name or user.username,
                "ecg": vitals.ecg,
                "spo2": vitals.spo2,
                "nibp": vitals.nibp,
                "rr": vitals.rr,
                "temp": vitals.temp,
                "status": "Active" if vitals.status != "Critical" else "Critical"
            })
        else:
            vitals_data.append({
                "username": user.username,
                "name": user.first_name or user.username,
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

        if not user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

        vitals, _ = Vitals.objects.get_or_create(user=user)
        vitals.ecg = data.get('ecg', vitals.ecg)
        vitals.spo2 = data.get('spo2', vitals.spo2)
        vitals.nibp = data.get('nibp', vitals.nibp)
        vitals.rr = data.get('rr', vitals.rr)
        vitals.temp = data.get('temp', vitals.temp)
        vitals.status = data.get('status', vitals.status)
        vitals.last_updated = timezone.now()
        vitals.save()

        status, _ = AmbulanceStatus.objects.get_or_create(user=user)
        status.is_active = True
        status.last_seen = timezone.now()
        status.save(update_fields=['is_active', 'last_seen'])

        print(f"[UPDATE] {user.username}: last_seen={status.last_seen}")

        return JsonResponse({'message': 'Vitals updated successfully'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# def get_all_vitals(request):
#     now = timezone.now()
#     timeout_seconds = 10

#     try:
#         ambulance_group = Group.objects.get(name='ambulance')
#         ambulance_users = ambulance_group.user_set.all()
#     except Group.DoesNotExist:
#         ambulance_users = []

#     data = []

#     for user in ambulance_users:
#         vitals = Vitals.objects.filter(user=user).order_by('-last_updated').first()
#         status_entry, _ = AmbulanceStatus.objects.get_or_create(user=user)

#         # Determine active/inactive
#         is_active = False
#         if status_entry.last_seen:
#             diff = (now - status_entry.last_seen).total_seconds()
#             if diff <= timeout_seconds:
#                 is_active = True
#             else:
#                 status_entry.is_active = False
#                 status_entry.save(update_fields=['is_active'])
#                 print(f"[TIMEOUT] {user.username}: No update for {diff:.1f}s (inactive).")
#         else:
#             print(f"[NO STATUS] {user.username}: Never seen active.")

#         # Compose output
#         if is_active and vitals:
#             data.append({
#                 'username': user.username,
#                 'name': user.first_name or user.username,
#                 'ecg': vitals.ecg,
#                 'spo2': vitals.spo2,
#                 'nibp': vitals.nibp,
#                 'rr': vitals.rr,
#                 'temp': vitals.temp,
#                 'status': 'Active' if vitals.status != 'Critical' else 'Critical'
#             })
#         else:
#             data.append({
#                 'username': user.username,
#                 'name': user.first_name or user.username,
#                 'ecg': '--',
#                 'spo2': '--',
#                 'nibp': '--',
#                 'rr': '--',
#                 'temp': '--',
#                 'status': 'Inactive'
#             })

#     return JsonResponse(data, safe=False)

def get_all_vitals(request):
    """
    Return latest vitals for all ambulances.
    If ambulance inactive > 10s, show '--' and status='Inactive'.
    """
    now = timezone.now()
    timeout_seconds = 10  # change here if you want a longer inactivity timeout

    ambulance_group = Group.objects.filter(name="ambulance").first()
    ambulance_users = ambulance_group.user_set.all() if ambulance_group else []

    response_data = []

    for user in ambulance_users:
        vitals = Vitals.objects.filter(user=user).first()
        status_entry = AmbulanceStatus.objects.filter(user=user).first()
        last_seen = status_entry.last_seen if status_entry else None

        # Determine active/inactive
        is_active = False
        if last_seen and (now - last_seen).total_seconds() <= timeout_seconds:
            is_active = True

        if not is_active:
            print(f"[INACTIVE] {user.username} no update for >{timeout_seconds}s")
            response_data.append({
                "username": user.username,
                "name": user.first_name or user.username,
                "ecg": "--",
                "spo2": "--",
                "nibp": "--",
                "rr": "--",
                "temp": "--",
                "status": "Inactive"
            })
        else:
            response_data.append({
                "username": user.username,
                "name": user.first_name or user.username,
                "ecg": vitals.ecg if vitals else "--",
                "spo2": vitals.spo2 if vitals else "--",
                "nibp": vitals.nibp if vitals else "--",
                "rr": vitals.rr if vitals else "--",
                "temp": vitals.temp if vitals else "--",
                "status": vitals.status if vitals else "Active"
            })

    return JsonResponse(response_data, safe=False)  