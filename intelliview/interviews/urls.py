from django.urls import path
from . import views

urlpatterns = [
    path('save-history/', views.save_interview_history, name='save-interview-history'),
    path('save-question/', views.save_question_answer, name='save-question-answer'),
] 