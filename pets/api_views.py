from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .filters import PetFilter
from .models import AdoptionRequest, Pet
from .serializers import AdoptionRequestSerializer, PetSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    """Anyone can read pets; only staff can create/update/delete."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or bool(request.user and request.user.is_staff)


class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PetFilter
    search_fields = ["name", "breed", "animal_type", "location", "description"]
    ordering_fields = ["created_at", "age", "name"]


class AdoptionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = AdoptionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]  # no DELETE

    def get_queryset(self):
        return AdoptionRequest.objects.filter(user=self.request.user).select_related("pet")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
