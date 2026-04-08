from django.urls import path
from . import views

urlpatterns = [
    path("start/<int:exam_id>/", views.start_exam, name="start_exam"),
    path("save-screenshot/", views.save_screenshot, name="save_screenshot"),
    path("detect-phone/", views.detect_phone_api, name="detect_phone"),
]