from django.db import models
from django.conf import settings

def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user.id}/{filename}"

class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to=resume_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s resume"

class Education(models.Model):
    resume = models.ForeignKey(Resume, related_name='education', on_delete=models.CASCADE)
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    start_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    gpa = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.degree} at {self.institution}"

class WorkExperience(models.Model):
    resume = models.ForeignKey(Resume, related_name='experience', on_delete=models.CASCADE)
    position = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.position} at {self.company}"

class Project(models.Model):
    resume = models.ForeignKey(Resume, related_name='projects', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    technologies = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name
