from django.urls import path
from . import views

urlpatterns = [

    path('register/', views.register, name="register"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),

    # FACE VERIFICATION PAGE
    path('verify-face/', views.face_verification, name="verify_face"),

    # SAVE FACE IMAGE
    path('save-face/', views.save_face, name="save_face"),

    # VERIFY FACE IDENTITY
    path('verify-face-identity/', views.verify_face_identity, name="verify_face_identity"),

]