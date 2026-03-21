from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Author, Subject, Tag, ContentItem
from .serializers import (
    AuthorSerializer,
    SubjectSerializer,
    TagSerializer,
    ContentItemListSerializer,
    ContentItemDetailSerializer,
)
from .filters import ContentItemFilter


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    search_fields = ["name"]


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    search_fields = ["name"]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ["name"]


class ContentItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentItem.objects.select_related("author", "subject").prefetch_related(
        "tags"
    )
    filterset_class = ContentItemFilter
    search_fields = ["title", "description", "author__name", "subject__name", "tags__name"]
    ordering_fields = ["title", "year", "created_at", "author__name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ContentItemDetailSerializer
        return ContentItemListSerializer

    @extend_schema(
        description="Check if a content item's remote file has changed based on stored hash",
        responses={200: {"type": "object", "properties": {
            "changed": {"type": "boolean"},
            "current_hash": {"type": "string"},
            "last_modified": {"type": "string", "format": "date-time"},
        }}},
    )
    @action(detail=True, methods=["get"])
    def check_update(self, request, pk=None):
        item = self.get_object()
        return Response({
            "changed": False,
            "current_hash": item.file_hash,
            "last_modified": item.last_modified_remote,
            "drive_file_id": item.drive_file_id,
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["username", "password"],
            }
        },
        responses={200: {"type": "object", "properties": {
            "token": {"type": "string"},
            "user_id": {"type": "integer"},
            "username": {"type": "string"},
        }}},
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
            })
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()
        return Response({"detail": "Logged out."})
