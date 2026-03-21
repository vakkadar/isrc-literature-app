from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthorViewSet,
    SubjectViewSet,
    TagViewSet,
    ContentItemViewSet,
    LoginView,
    LogoutView,
)

router = DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("subjects", SubjectViewSet)
router.register("tags", TagViewSet)
router.register("content", ContentItemViewSet)

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
    path("", include(router.urls)),
]
