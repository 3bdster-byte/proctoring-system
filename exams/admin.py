from django.contrib import admin
from .models import Exam, Question, Result, ExamAttempt, CheatingScreenshot


# ==============================
# EXAM ADMIN
# ==============================

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'start_time', 'end_time')
    search_fields = ('title',)
    list_filter = ('start_time', 'end_time')


# ==============================
# QUESTION ADMIN
# ==============================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question_text', 'correct_answer')
    search_fields = ('question_text',)
    list_filter = ('exam',)


# ==============================
# RESULT ADMIN
# ==============================

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'total_questions', 'submitted_at')
    list_filter = ('exam', 'submitted_at')
    search_fields = ('student__username', 'exam__title')


# ==============================
# EXAM ATTEMPT ADMIN
# ==============================

@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'exam', 'score',
        'tab_warnings', 'face_warnings', 'phone_warnings',
        'date'
    )
    list_filter = ('exam', 'date')
    search_fields = ('student__username', 'exam__title')


# ==============================
# CHEATING SCREENSHOT ADMIN
# ==============================

@admin.register(CheatingScreenshot)
class CheatingScreenshotAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'reason', 'created_at')
    list_filter = ('exam', 'created_at', 'reason')
    search_fields = ('student__username', 'exam__title', 'reason')