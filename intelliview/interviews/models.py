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

class InterviewHistoryData(models.Model):
    """
    Model to store interview question, answer, feedback and score data
    """
    session = models.ForeignKey(InterviewSession, related_name='history_data', on_delete=models.CASCADE)
    question_text = models.TextField()
    answer_text = models.TextField(blank=True)  # Allow blank but not null
    feedback = models.TextField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Interview History Data"
        verbose_name_plural = "Interview History Data"

    def __str__(self):
        return f"Question: {self.question_text[:30]}... - Score: {self.score or 'N/A'}" 