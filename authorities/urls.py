from rest_framework.routers import DefaultRouter
from .views import OversightAuthorityViewSet

router = DefaultRouter()
router.register("authorities", OversightAuthorityViewSet, basename="authorities")

urlpatterns = router.urls