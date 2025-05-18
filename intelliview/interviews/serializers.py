from rest_framework import serializers
from .models import InterviewSession, InterviewHistoryData

class InterviewHistoryDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewHistoryData
        fields = [
            'id', 'session', 'question_text', 'answer_text', 
            'feedback', 'score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class InterviewSessionSerializer(serializers.ModelSerializer):
    history_data = InterviewHistoryDataSerializer(many=True, read_only=True)
    
    class Meta:
        model = InterviewSession
        fields = ['id', 'user', 'questions', 'started_at', 'completed', 'score', 'history_data']
        read_only_fields = ['id', 'started_at'] 