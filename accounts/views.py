from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.base import ContentFile

import base64
import json
import cv2
import numpy as np

from deepface import DeepFace

from exams.models import Exam
from .models import StudentProfile


# ==============================
# REGISTER
# ==============================

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        face_image = request.POST.get("face_image")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        # SAVE FACE IMAGE
        if face_image:
            format, imgstr = face_image.split(';base64,')
            ext = format.split('/')[-1]

            file = ContentFile(
                base64.b64decode(imgstr),
                name="face." + ext
            )

            StudentProfile.objects.create(
                user=user,
                face_image=file
            )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'accounts/register.html')


# ==============================
# LOGIN
# ==============================

def user_login(request):
    # If already logged in, check whether face verification is completed
    if request.user.is_authenticated:
        if request.session.get("face_verified", False):
            return redirect('dashboard')
        return redirect('verify_face')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Every fresh login must go through face verification
            request.session["face_verified"] = False

            # Session ends when browser closes
            request.session.set_expiry(0)

            return redirect('verify_face')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


# ==============================
# FACE VERIFICATION PAGE
# ==============================

@login_required
def face_verification(request):
    return render(request, "accounts/face_verification.html")


# ==============================
# SAVE FACE API
# ==============================

@login_required
def save_face(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data.get("image")

        if not image_data:
            return JsonResponse({"status": "no image"})

        format, imgstr = image_data.split(";base64,")
        ext = format.split("/")[-1]

        file = ContentFile(
            base64.b64decode(imgstr),
            name="face." + ext
        )

        profile, created = StudentProfile.objects.get_or_create(
            user=request.user
        )

        profile.face_image = file
        profile.save()

        return JsonResponse({"status": "saved"})

    return JsonResponse({"status": "invalid request"})


# ==============================
# VERIFY FACE IDENTITY
# ==============================

@login_required
def verify_face_identity(request):
    if request.method == "POST":
        data = json.loads(request.body)
        image_data = data.get("image")

        if not image_data:
            return JsonResponse({"verified": False})

        format, imgstr = image_data.split(";base64,")
        img_bytes = base64.b64decode(imgstr)

        np_arr = np.frombuffer(img_bytes, np.uint8)
        captured_face = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # SAFE PROFILE FETCH
        profile, created = StudentProfile.objects.get_or_create(
            user=request.user
        )

        # If face not stored yet → save it automatically
        if not profile.face_image:
            file = ContentFile(
                img_bytes,
                name="face_auto.jpg"
            )

            profile.face_image = file
            profile.save()

            request.session["face_verified"] = True

            return JsonResponse({
                "verified": True,
                "message": "Face registered successfully"
            })

        # VERIFY FACE USING AI
        result = DeepFace.verify(
            captured_face,
            profile.face_image.path,
            enforce_detection=False
        )

        if result["verified"]:
            request.session["face_verified"] = True
        else:
            request.session["face_verified"] = False

        return JsonResponse({
            "verified": result["verified"]
        })

    return JsonResponse({"verified": False})


# ==============================
# DASHBOARD
# ==============================

@login_required(login_url='login')
def dashboard(request):
    # Block dashboard until face verification is completed
    if not request.session.get("face_verified", False):
        return redirect('verify_face')

    exams = Exam.objects.all()

    return render(request, 'accounts/dashboard.html', {
        'exams': exams
    })


# ==============================
# LOGOUT
# ==============================

def user_logout(request):
    request.session.flush()
    logout(request)

    messages.success(request, "You logged out successfully")

    return redirect('login')