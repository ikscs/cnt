#base.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from rest_framework.permissions import IsAuthenticated
from pcnt.authentication import UserfrontAuthentication

#Full CRUD views
class PCNTBaseViewSet(viewsets.ModelViewSet):
    authentication_classes = [UserfrontAuthentication]
    permission_classes = [IsAuthenticated]

#Function-based logic
class PCNTBaseAPIView(APIView):
    authentication_classes = [UserfrontAuthentication]
    permission_classes = [IsAuthenticated]

#Custom action views
class PCNTBaseActionViewSet(ViewSet):
    authentication_classes = [UserfrontAuthentication]
    permission_classes = [IsAuthenticated]

#Read-only views
class PCNTBaseReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [UserfrontAuthentication]
    permission_classes = [IsAuthenticated]
