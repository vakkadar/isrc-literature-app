from django_filters import rest_framework as filters
from .models import ContentItem, Collection


class ContentItemFilter(filters.FilterSet):
    person = filters.NumberFilter(field_name="person__id")
    category = filters.NumberFilter(field_name="category__id")
    language = filters.NumberFilter(field_name="language__id")
    content_type = filters.CharFilter()
    collection = filters.NumberFilter(field_name="collection__id")
    year = filters.NumberFilter()

    class Meta:
        model = ContentItem
        fields = ["person", "category", "language", "content_type", "collection", "year"]


class CollectionFilter(filters.FilterSet):
    person = filters.NumberFilter(field_name="person__id")
    category = filters.NumberFilter(field_name="category__id")
    language = filters.NumberFilter(field_name="language__id")

    class Meta:
        model = Collection
        fields = ["person", "category", "language"]
