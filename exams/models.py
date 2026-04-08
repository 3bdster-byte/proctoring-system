from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")

    # New fields for scheduled exam timing
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def is_live(self):
        if self.start_time and self.end_time:
            now = timezone.now()
            return self.start_time <= now <= self.end_time
        return False

    def has_started(self):
        if self.start_time:
            return timezone.now() >= self.start_time
        return False

    def has_ended(self):
        if self.end_time:
            return timezone.now() > self.end_time
        return False

    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_text = models.TextField()

    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)

    correct_answer = models.IntegerField(help_text="Enter option number (1-4)")

    def __str__(self):
        return self.question_text


class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    score = models.IntegerField()
    total_questions = models.IntegerField()

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} ({self.score}/{self.total_questions})"


class ExamAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)

    score = models.IntegerField(default=0)

    tab_warnings = models.IntegerField(default=0)
    face_warnings = models.IntegerField(default=0)
    phone_warnings = models.IntegerField(default=0)

    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"


class CheatingScreenshot(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cheating_screenshots"
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="cheating_screenshots"
    )

    image = models.ImageField(upload_to="cheating_screenshots/")

    reason = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {self.reason}"