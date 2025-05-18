from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests
import json
import os
import time

# LLM Service URL - get from environment or use a default
LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'https://5b98-49-207-59-237.ngrok-free.app')

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint to verify the API is running
    """
    return Response({
        'status': 'ok',
        'message': 'API is up and running'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def llm_health_check(request):
    """
    Check if the LLM service is reachable by calling its /health endpoint
    """
    try:
        # Use the correct health endpoint on the LLM server
        target_url = f"{LLM_SERVICE_URL.rstrip('/')}/health"
        
        # Log for debugging
        print(f"Checking LLM service health at: {target_url}")
        
        # Make the request
        response = requests.get(
            target_url,
            headers={'Content-Type': 'application/json'},
            timeout=5  # Short timeout for health check
        )
        
        if response.status_code == 200:
            return Response({
                'status': 'ok',
                'message': 'LLM service is up and running'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': f'LLM service returned status code {response.status_code}'
            }, status=status.HTTP_502_BAD_GATEWAY)
            
    except requests.RequestException as e:
        return Response({
            'status': 'error',
            'message': f'Error connecting to LLM service: {str(e)}'
        }, status=status.HTTP_502_BAD_GATEWAY)

@api_view(['POST'])
@permission_classes([AllowAny])
def llm_service_proxy(request, endpoint=None):
    """
    Proxy requests to the LLM service to help with CORS issues
    """
    if not endpoint:
        return Response({"error": "No endpoint specified"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Maximum number of retries
    max_retries = 2
    current_retry = 0
    last_error = None
    
    while current_retry <= max_retries:
        try:
            # Clean the endpoint path
            # 1. Remove 'api/' from the beginning of the endpoint if it exists
            if endpoint.startswith('api/'):
                endpoint = endpoint[4:]
            # 2. Remove any leading slash
            elif endpoint.startswith('/'):
                endpoint = endpoint[1:]
            
            # Build the target URL for the LLM service, ensuring api/ is included
            target_url = f"{LLM_SERVICE_URL.rstrip('/')}/api/{endpoint}"
            
            # Log the proxy request for debugging
            print(f"Proxying request to: {target_url} (Attempt {current_retry + 1}/{max_retries + 1})")
            print(f"Request data: {request.data}")
            
            # Forward the request to the LLM service
            response = requests.post(
                target_url,
                json=request.data,
                headers={
                    'Content-Type': 'application/json',
                },
                timeout=90  # 90 second timeout for longer LLM operations
            )
            
            # Log the response for debugging
            print(f"LLM proxy response ({target_url}): {response.status_code}")
            
            # Return the response from the LLM service
            try:
                data = response.json()
                return Response(data, status=response.status_code)
            except json.JSONDecodeError:
                # If response is not JSON, return text
                return Response(
                    {"error": f"Invalid JSON response: {response.text}"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
                
        except requests.RequestException as e:
            last_error = str(e)
            print(f"Error connecting to LLM service (Attempt {current_retry + 1}/{max_retries + 1}): {last_error}")
            current_retry += 1
            
            # If we're at the maximum retries, break out
            if current_retry > max_retries:
                break
                
            # Wait a bit before trying again (exponential backoff)
            time.sleep(2 ** current_retry)  # 2, 4, 8 seconds...
    
    # If we get here, all retries failed
    return Response(
        {
            "error": f"Error connecting to LLM service after {max_retries + 1} attempts",
            "details": last_error
        },
        status=status.HTTP_502_BAD_GATEWAY
    ) 