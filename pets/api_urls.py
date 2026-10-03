from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import AdoptionRequestViewSet, PetViewSet

router = DefaultRouter()
router.register("pets", PetViewSet, basename="pet")
router.register("adoptions", AdoptionRequestViewSet, basename="adoption")

urlpatterns = [path("", include(router.urls))]
