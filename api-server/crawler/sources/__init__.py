from .archive import ArchiveOrgSource
from .base import BaseSource, RawHit, SourceConfigError, SourceError
from .google_books import GoogleBooksSource
from .open_library import OpenLibrarySource
from .podcast import ListenNotesSource
from .web import OfficialSiteSource, WebSource
from .youtube import YouTubeSource

REGISTRY: dict[str, type[BaseSource]] = {
    WebSource.code: WebSource,
    OfficialSiteSource.code: OfficialSiteSource,
    ArchiveOrgSource.code: ArchiveOrgSource,
    YouTubeSource.code: YouTubeSource,
    GoogleBooksSource.code: GoogleBooksSource,
    OpenLibrarySource.code: OpenLibrarySource,
    ListenNotesSource.code: ListenNotesSource,
}


def get_source(source_model) -> BaseSource:
    cls = REGISTRY.get(source_model.code)
    if cls is None:
        raise SourceError(f"No source class registered for code={source_model.code!r}")
    return cls(source_model)


__all__ = [
    "REGISTRY",
    "RawHit",
    "BaseSource",
    "SourceError",
    "SourceConfigError",
    "get_source",
    "WebSource",
    "OfficialSiteSource",
    "ArchiveOrgSource",
    "YouTubeSource",
    "GoogleBooksSource",
    "OpenLibrarySource",
    "ListenNotesSource",
]
