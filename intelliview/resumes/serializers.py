from rest_framework import serializers
from .models import Resume, Education, WorkExperience, Project

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'start_date', 'end_date', 'gpa']

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'position', 'company', 'start_date', 'end_date', 'description']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'technologies']

class ResumeSerializer(serializers.ModelSerializer):
    education = EducationSerializer(many=True, read_only=True)
    experience = WorkExperienceSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Resume
        fields = ['id', 'file', 'uploaded_at', 'parsed', 'education', 'experience', 'projects']
        read_only_fields = ['uploaded_at', 'parsed']
