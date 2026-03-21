from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PersonViewSet,
    LanguageViewSet,
    CategoryViewSet,
    TagViewSet,
    CollectionViewSet,
    ContentItemViewSet,
    DiscoveryViewSet,
    LoginView,
    LogoutView,
)

router = DefaultRouter()
router.register("persons", PersonViewSet)
router.register("languages", LanguageViewSet)
router.register("categories", CategoryViewSet)
router.register("tags", TagViewSet)
router.register("collections", CollectionViewSet)
router.register("content", ContentItemViewSet)
router.register("discoveries", DiscoveryViewSet)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
    path("", include(router.urls)),
]
