from django_filters import rest_framework as filters
from .models import ContentItem


class ContentItemFilter(filters.FilterSet):
    author = filters.NumberFilter(field_name="author__id")
    author_name = filters.CharFilter(field_name="author__name", lookup_expr="icontains")
    subject = filters.NumberFilter(field_name="subject__id")
    subject_name = filters.CharFilter(field_name="subject__name", lookup_expr="icontains")
    year = filters.NumberFilter()
    year_min = filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = filters.NumberFilter(field_name="year", lookup_expr="lte")
    content_type = filters.CharFilter()
    tag = filters.CharFilter(field_name="tags__name", lookup_expr="icontains")

    class Meta:
        model = ContentItem
        fields = [
            "author",
            "author_name",
            "subject",
            "subject_name",
            "year",
            "year_min",
            "year_max",
            "content_type",
            "tag",
        ]
