from rest_framework import serializers
from .models import (
    Person, Language, Category, Tag, Collection, ContentItem, Discovery, CrawlerSearchTerm,
)


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["id", "name", "role", "description"]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["id", "name", "code"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class CollectionSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    language_code = serializers.CharField(source="language.code", read_only=True)

    class Meta:
        model = Collection
        fields = [
            "id", "title", "person", "person_name", "category", "category_name",
            "language", "language_code", "description", "year",
        ]


class CollectionDetailSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    language = LanguageSerializer(read_only=True)

    class Meta:
        model = Collection
        fields = [
            "id", "title", "person", "category", "language", "description", "year",
        ]


class ContentItemListSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    language_code = serializers.CharField(source="language.code", read_only=True, default=None)
    collection_title = serializers.CharField(
        source="collection.title", read_only=True, default=None
    )
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentItem
        fields = [
            "id", "title", "person", "person_name", "category", "category_name",
            "language", "language_code", "collection", "collection_title",
            "content_type", "file_url", "external_url", "description",
            "year", "chapter_number", "duration_seconds", "file_size_bytes",
            "created_at",
        ]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ContentItemDetailSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    collection = CollectionSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentItem
        fields = [
            "id", "title", "collection", "person", "category", "language", "tags",
            "content_type", "file_url", "source_url", "external_url", "description",
            "year", "chapter_number", "duration_seconds", "file_size_bytes",
            "created_at", "updated_at",
        ]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ContentItemNestedSerializer(serializers.ModelSerializer):
    """Compact serializer used when nesting items inside a collection."""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ContentItem
        fields = [
            "id", "title", "content_type", "file_url", "external_url",
            "chapter_number", "duration_seconds", "file_size_bytes",
        ]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class CollectionWithItemsSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    language = LanguageSerializer(read_only=True)
    items = ContentItemNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = [
            "id", "title", "person", "category", "language", "description", "year",
            "items",
        ]


class DiscoverySerializer(serializers.ModelSerializer):
    person_mentioned_name = serializers.CharField(
        source="person_mentioned.name", read_only=True, default=None
    )

    class Meta:
        model = Discovery
        fields = [
            "id", "title", "url", "source", "content_type", "snippet",
            "thumbnail_url", "person_mentioned", "person_mentioned_name",
            "search_term_used", "status", "discovered_at", "reviewed_at",
        ]


class CrawlerSearchTermSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.name", read_only=True, default=None)

    class Meta:
        model = CrawlerSearchTerm
        fields = ["id", "term", "person", "person_name", "enabled", "last_searched"]
