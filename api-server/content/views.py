from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import (
    Person, Language, Category, Tag, Collection, ContentItem, Discovery,
)
from .serializers import (
    PersonSerializer,
    LanguageSerializer,
    CategorySerializer,
    TagSerializer,
    CollectionSerializer,
    CollectionWithItemsSerializer,
    ContentItemListSerializer,
    ContentItemDetailSerializer,
    DiscoverySerializer,
)
from .filters import ContentItemFilter, CollectionFilter


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    search_fields = ["name"]


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    search_fields = ["name", "code"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ["name"]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ["name"]


class CollectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Collection.objects.select_related("person", "category", "language").prefetch_related(
        "items"
    )
    filterset_class = CollectionFilter
    search_fields = ["title", "description", "person__name"]
    ordering_fields = ["title", "year"]
    ordering = ["title"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CollectionWithItemsSerializer
        return CollectionSerializer


class ContentItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentItem.objects.select_related(
        "person", "category", "language", "collection"
    ).prefetch_related("tags")
    filterset_class = ContentItemFilter
    search_fields = ["title", "description", "person__name", "tags__name"]
    ordering_fields = ["title", "year", "created_at", "chapter_number"]
    ordering = ["collection", "chapter_number", "-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ContentItemDetailSerializer
        return ContentItemListSerializer


class DiscoveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Discovery.objects.select_related("person_mentioned").filter(status="pending")
    serializer_class = DiscoverySerializer
    search_fields = ["title", "snippet"]
    ordering = ["-discovered_at"]


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
