from django.db import models
from django.conf import settings

def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user.id}/{filename}"

class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to=resume_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s resume"
