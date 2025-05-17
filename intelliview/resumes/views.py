# Create your views here.
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import ResumeSerializer
from .models import Resume

class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResumeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumes = Resume.objects.filter(user=request.user)
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)

