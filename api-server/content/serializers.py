from rest_framework import serializers
from .models import Author, Subject, Tag, ContentItem


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "description"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ["id", "name", "description"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ContentItemListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = ContentItem
        fields = [
            "id",
            "title",
            "author",
            "author_name",
            "subject",
            "subject_name",
            "year",
            "tags",
            "content_type",
            "drive_file_id",
            "duration_seconds",
            "file_size_bytes",
            "description",
            "created_at",
        ]


class ContentItemDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = ContentItem
        fields = [
            "id",
            "title",
            "author",
            "subject",
            "year",
            "tags",
            "content_type",
            "drive_file_id",
            "drive_url",
            "file_hash",
            "last_modified_remote",
            "duration_seconds",
            "file_size_bytes",
            "description",
            "created_at",
            "updated_at",
        ]
