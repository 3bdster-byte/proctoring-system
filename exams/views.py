from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone

import json
import base64
import cv2
import numpy as np

from .models import Exam, Question, Result, ExamAttempt, CheatingScreenshot
from .phone_detector import detect_phone


# ==============================
# START EXAM
# ==============================

@login_required
def start_exam(request, exam_id):
    if not request.session.get("face_verified", False):
        return redirect('verify_face')

    exam = get_object_or_404(Exam, id=exam_id)

    if exam.start_time and timezone.now() < exam.start_time:
        messages.error(request, "This exam has not started yet.")
        return redirect('dashboard')

    if exam.end_time and timezone.now() > exam.end_time:
        messages.error(request, "This exam time is over.")
        return redirect('dashboard')

    session_key = f"exam_{exam_id}_question_ids"

    if request.method == "POST":
        question_ids = request.session.get(session_key, [])

        questions = Question.objects.filter(
            id__in=question_ids,
            exam=exam
        )

        score = 0

        for question in questions:
            selected = request.POST.get(str(question.id))

            if selected and str(selected).strip() == str(question.correct_answer).strip():
                score += 1

        total_questions = questions.count()

        Result.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            total_questions=total_questions
        )

        tab_warnings = int(request.POST.get("tab_warnings") or 0)
        face_warnings = int(request.POST.get("face_warnings") or 0)
        phone_warnings = int(request.POST.get("phone_warnings") or 0)

        ExamAttempt.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            tab_warnings=tab_warnings,
            face_warnings=face_warnings,
            phone_warnings=phone_warnings
        )

        if session_key in request.session:
            del request.session[session_key]

        return render(request, "exams/result.html", {
            "score": score,
            "total": total_questions
        })

    # GET request
    all_question_ids = list(
        Question.objects.filter(exam=exam).values_list('id', flat=True)
    )

    total_uploaded = len(all_question_ids)
    questions_to_show = max(1, total_uploaded // 2)

    question_ids = request.session.get(session_key)

    if not question_ids:
        question_ids = list(
            Question.objects.filter(exam=exam)
            .order_by('?')
            .values_list('id', flat=True)[:questions_to_show]
        )
        request.session[session_key] = question_ids

    questions = Question.objects.filter(
        id__in=question_ids,
        exam=exam
    )

    return render(request, "exams/exam_page.html", {
        "exam": exam,
        "questions": questions
    })


# ==============================
# SAVE CHEATING SCREENSHOT
# ==============================

@csrf_exempt
@login_required
def save_screenshot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "invalid json"})

        image_data = data.get("image")
        reason = data.get("reason")
        exam_id = data.get("exam_id")

        if not image_data:
            return JsonResponse({"error": "no image"})

        exam = get_object_or_404(Exam, id=exam_id)

        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
        except:
            return JsonResponse({"error": "invalid image format"})

        file = ContentFile(
            base64.b64decode(imgstr),
            name="cheating." + ext
        )

        CheatingScreenshot.objects.create(
            student=request.user,
            exam=exam,
            image=file,
            reason=reason
        )

        return JsonResponse({"status": "saved"})

    return JsonResponse({"status": "invalid request"})


# ==============================
# PHONE DETECTION API
# ==============================

@csrf_exempt
@login_required
def detect_phone_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"phone": False})

        image_data = data.get("image")

        if not image_data:
            return JsonResponse({"phone": False})

        try:
            format, imgstr = image_data.split(";base64,")
            img_bytes = base64.b64decode(imgstr)
        except:
            return JsonResponse({"phone": False})

        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        try:
            phone_detected = detect_phone(frame)
        except Exception as e:
            print("Detection error:", e)
            phone_detected = False

        return JsonResponse({
            "phone": phone_detected
        })

    return JsonResponse({"phone": False})