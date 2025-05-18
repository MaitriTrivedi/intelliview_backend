from django.urls import path
from .views import ResumeUploadView, ResumeListView, ResumeParseView

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('my/', ResumeListView.as_view(), name='resume-list'),
    path('parse/', ResumeParseView.as_view(), name='resume-parse'),
]
