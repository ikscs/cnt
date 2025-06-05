from django.shortcuts import render
from rest_framework.test import APIClient
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Login form view
def login_form(request):
    token = None
    error = None
    test_result = None

    if request.method == 'POST':
        client = APIClient()

        if 'login' in request.POST:
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Obtain token pair
            response = client.post('/api/token/', {
                'username': username,
                'password': password
            }, format='json')

            if response.status_code == 200:
                token = response.data.get('access')
            else:
                error = response.data.get('detail', 'Login failed')

        elif 'test_token' in request.POST:
            token = request.POST.get('token')
            if token:
                # Set token in Authorization header
                client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                # Call protected endpoint to verify token
                response = client.get('/api/authdemo/token-check/')
                if response.status_code == 200:
                    test_result = '✅ Token is valid (via Authorization header).'
                else:
                    test_result = f'❌ Token invalid or expired (HTTP {response.status_code})'
            else:
                test_result = '⚠️ No token provided.'

        elif 'logout' in request.POST:
            token = None
            test_result = '🧼 Logged out.'

    return render(request, 'authdemo/login.html', {
        'token': token,
        'error': error,
        'test_result': test_result,
    })


# Protected view to test token validity
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({'message': f"Hello, {request.user.username}! Token is valid."})
