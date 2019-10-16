from django.db import models
from django.contrib.auth.models import User


class AnswerModel(models.Model):
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)


class QuestionModel(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="questions_owner")
    asked_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="questions_asked")
    content = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)
    answer = models.OneToOneField(
        AnswerModel, null=True, on_delete=models.CASCADE)
