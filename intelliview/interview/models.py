from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class InterviewSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = models.JSONField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s session on {self.started_at.strftime('%Y-%m-%d %H:%M')}"
