from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import InterviewSession, InterviewHistoryData
from .serializers import InterviewSessionSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_question_answer(request):
    """
    Save a single question-answer with feedback and score after evaluation
    """
    try:
        # Get required data from request
        question_text = request.data.get('question', '')
        answer_text = request.data.get('answer', '')
        feedback = request.data.get('feedback', '')
        score = request.data.get('score')
        session_id = request.data.get('session_id')
        
        # Ensure answer_text is never null
        if answer_text is None:
            answer_text = ''
            
        # Find or create a session
        if session_id:
            try:
                session = InterviewSession.objects.get(id=session_id, user=request.user)
            except InterviewSession.DoesNotExist:
                # Create new session if none exists with that ID
                session = InterviewSession.objects.create(
                    user=request.user,
                    questions={},
                    completed=False
                )
        else:
            # Create a new session if no ID provided
            session = InterviewSession.objects.create(
                user=request.user,
                questions={},
                completed=False
            )
        
        # Create the history data entry
        history_entry = InterviewHistoryData.objects.create(
            session=session,
            question_text=question_text,
            answer_text=answer_text,
            feedback=feedback,
            score=score
        )
        
        # Update session score with average of all questions
        all_questions = InterviewHistoryData.objects.filter(session=session)
        valid_scores = [q.score for q in all_questions if q.score is not None]
        
        if valid_scores:
            session.score = sum(valid_scores) / len(valid_scores)
            session.save()
        
        return Response({
            "success": True,
            "message": "Question and answer saved successfully",
            "session_id": session.id,
            "entry_id": history_entry.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_interview_history(request):
    """
    Save detailed interview history data including questions, answers, feedback and scores
    """
    try:
        # First, find or create an interview session
        session_id = request.data.get('session_id')
        
        if session_id:
            try:
                session = InterviewSession.objects.get(id=session_id, user=request.user)
            except InterviewSession.DoesNotExist:
                return Response(
                    {"error": "Interview session not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create a new session if none exists
            session = InterviewSession.objects.create(
                user=request.user,
                questions={},  # Empty JSON
                completed=False
            )
        
        # Get the questions data from the request
        questions_data = request.data.get('questions', [])
        
        if not questions_data:
            return Response(
                {"error": "No questions data provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate overall score for session
        total_score = 0
        valid_scores = 0
            
        # Process each question and save it to the database
        for idx, question_data in enumerate(questions_data):
            # Extract data from the question
            question_text = question_data.get('text', '')
            answer_text = question_data.get('answer', '')
            
            # Ensure answer_text is never null - use empty string if no answer provided
            if answer_text is None:
                answer_text = ''
            
            # Extract evaluation data if available
            evaluation = question_data.get('evaluation', {})
            score = evaluation.get('score') if evaluation else None
            feedback = evaluation.get('feedback', '') if evaluation else ''
            
            # Track scores for calculation
            if score is not None:
                total_score += float(score)
                valid_scores += 1
                
            # Save to InterviewHistoryData
            InterviewHistoryData.objects.create(
                session=session,
                question_text=question_text,
                answer_text=answer_text,
                feedback=feedback,
                score=score
            )
        
        # Update the session with completed status and overall score
        if valid_scores > 0:
            session.score = total_score / valid_scores
        session.questions = {"count": len(questions_data)}
        session.completed = True
        session.save()
        
        return Response({
            "success": True,
            "message": "Interview history saved successfully",
            "session_id": session.id,
            "score": session.score
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 