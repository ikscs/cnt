#base.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import NotFound
from rest_framework import mixins

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

#Full CRUD views for No PK table
class PCNTBaseNoPkViewSet(
    mixins.ListModelMixin,        # GET
    mixins.RetrieveModelMixin,    # GET
    mixins.CreateModelMixin,      # POST
    mixins.UpdateModelMixin,      # PUT/PATCH
    mixins.DestroyModelMixin,     # DELETE
    viewsets.GenericViewSet
    ):

    authentication_classes = [UserfrontAuthentication]
    permission_classes = [IsAuthenticated]

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    #model_class = ... #Weak
    #queryset = ...objects.all() #Weak
    #serializer_class = ...Serializer #Weak

    def get_queryset(self):
        return self.model_class.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        lookup = {k.name: self.kwargs.get(k.name) for k in self.model_class._meta.pk.fields}

        try:
            return queryset.get(**lookup)
        except self.model_class.DoesNotExist:
            raise NotFound("Object not found.")
