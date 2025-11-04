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

import base64, time, json
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.utils import timezone
from .models import ServerKeys, UserPublicKey
from .crypto_helpers import MockKyber, MockDilithium, hkdf_derive


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





@csrf_exempt
def get_server_keys(request):
    """Return the hospital’s public Kyber + ECC keys."""
    sk = ServerKeys.objects.first()
    if not sk:
        return JsonResponse({"error": "Server keys not initialized"}, status=500)
    return JsonResponse({"kyber_public": sk.kyber_public, "ecdh_public": sk.ecdh_public})


@csrf_exempt
def register_ambulance_key(request):
    """Ambulance registers its Dilithium public key once."""
    data = json.loads(request.body)
    username = data.get("username")
    pubkey = data.get("dilithium_public")
    if not username or not pubkey:
        return JsonResponse({"error": "missing fields"}, status=400)
    user = User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({"error": "user not found"}, status=404)
    UserPublicKey.objects.update_or_create(user=user, defaults={"dilithium_public": pubkey})
    return JsonResponse({"status": "registered"})


# @csrf_exempt
# def update_vitals_secure(request):
#     """
#     Secure vitals endpoint (Hybrid PQC)
#     Expect JSON:
#       ambulance_id, timestamp, ct_kyber, ecdh_pub, nonce, ciphertext, signature
#     """
#     try:
#         payload = json.loads(request.body)
#     except Exception:
#         return JsonResponse({"error": "invalid json"}, status=400)

#     amb_id = payload.get("ambulance_id")
#     ts = payload.get("timestamp")
#     if not amb_id or not ts:
#         return JsonResponse({"error": "missing ambulance_id or timestamp"}, status=400)

#     # Freshness check
#     if abs(time.time() - float(ts)) > 120:
#         return JsonResponse({"error": "stale message"}, status=400)

#     user = User.objects.filter(username=amb_id).first()
#     if not user:
#         return JsonResponse({"error": "unknown ambulance"}, status=404)

#     # Verify signature
#     upk = UserPublicKey.objects.filter(user=user).first()
#     if not upk:
#         return JsonResponse({"error": "no public key registered"}, status=403)

#     msg = (payload["ambulance_id"] + "|" + str(payload["timestamp"]) + "|" +
#            payload["ct_kyber"] + "|" + payload["ecdh_pub"] + "|" +
#            payload["nonce"] + "|" + payload["ciphertext"]).encode()
#     if not MockDilithium.verify(msg, payload["signature"], upk.dilithium_public):
#         return JsonResponse({"error": "bad signature"}, status=403)

#     # Derive shared secrets
#     sk = ServerKeys.objects.first()
#     if not sk:
#         return JsonResponse({"error": "server keys missing"}, status=500)

#     kem = MockKyber()
#     ss_kyber = base64.b64decode(kem.decap(payload["ct_kyber"], sk.kyber_private))

#     server_priv = x25519.X25519PrivateKey.from_private_bytes(base64.b64decode(sk.ecdh_private))
#     client_pub = x25519.X25519PublicKey.from_public_bytes(base64.b64decode(payload["ecdh_pub"]))
#     ss_ecc = server_priv.exchange(client_pub)

#     key = hkdf_derive(ss_kyber + ss_ecc, 32)

#     # Decrypt AES-GCM
#     aes = AESGCM(key)
#     try:
#         plaintext = aes.decrypt(base64.b64decode(payload["nonce"]),
#                                 base64.b64decode(payload["ciphertext"]), None)
#         vitals_json = json.loads(plaintext.decode())
#     except Exception as e:
#         return JsonResponse({"error": "decryption failed", "detail": str(e)}, status=400)

#     # Store vitals
#     v, _ = Vitals.objects.get_or_create(user=user)
#     for field in ['ecg','spo2','nibp','rr','temp','status']:
#         if field in vitals_json:
#             setattr(v, field, vitals_json[field])
#     v.last_updated = timezone.now()
#     v.save()

#     s, _ = AmbulanceStatus.objects.get_or_create(user=user)
#     s.is_active = True
#     s.last_seen = timezone.now()
#     s.save(update_fields=['is_active','last_seen'])

#     return JsonResponse({"status": "secure vitals stored"})


@csrf_exempt
def update_vitals_secure(request):
    """Receive mock secure vitals (unverified) from ambulance dashboard."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    ambulance_id = data.get('ambulance_id')
    if not ambulance_id:
        return JsonResponse({'error': 'missing ambulance_id'}, status=400)

    user = User.objects.filter(username=ambulance_id).first()
    if not user:
        return JsonResponse({'error': 'unknown ambulance'}, status=404)

    # Save vitals
    v, _ = Vitals.objects.get_or_create(user=user)
    v.ecg = data.get('ecg', v.ecg)
    v.spo2 = data.get('spo2', v.spo2)
    v.nibp = data.get('nibp', v.nibp)
    v.rr = data.get('rr', v.rr)
    v.temp = data.get('temp', v.temp)
    v.status = data.get('status', v.status)
    v.last_updated = timezone.now()
    v.save()

    s, _ = AmbulanceStatus.objects.get_or_create(user=user)
    s.is_active = True
    s.last_seen = timezone.now()
    s.save(update_fields=['is_active', 'last_seen'])

    print(f"[SECURE UPDATE] {user.username}: {data.get('status')} @ {s.last_seen}")

    return JsonResponse({'status': 'secure vitals stored'})
