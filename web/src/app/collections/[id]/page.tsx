"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useAudio, collectionItemsToTracks } from "@/contexts/AudioContext";
import { getCollection } from "@/services/api";
import type { CollectionDetail, ContentItemNested } from "@/types";

function formatDuration(seconds: number | null): string {
  if (!seconds) return "—";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}:${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function totalDuration(items: ContentItemNested[]): string {
  const total = items.reduce((sum, i) => sum + (i.duration_seconds || 0), 0);
  if (!total) return "";
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  if (h > 0) return `${h}h ${m}m total`;
  return `${m} min total`;
}

export default function CollectionDetailPage() {
  const { loading: authLoading } = useAuth();
  const params = useParams();
  const router = useRouter();
  const { play, playCollection, currentTrack, isPlaying, togglePlay } = useAudio();

  const [collection, setCollection] = useState<CollectionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    const id = Number(params.id);
    getCollection(id)
      .then(setCollection)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [params.id, authLoading]);

  if (loading || authLoading) {
    return (
      <div className="flex justify-center py-32">
        <div className="w-8 h-8 border-3 border-saffron border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!collection) {
    return (
      <div className="text-center py-20">
        <div className="text-4xl mb-3">😕</div>
        <p className="text-warm-gray">Collection not found.</p>
        <button
          onClick={() => router.back()}
          className="mt-4 text-sm text-saffron-dark font-medium hover:text-saffron"
        >
          ← Go back
        </button>
      </div>
    );
  }

  const audioItems = collection.items.filter(
    (i) => i.content_type === "audio" && i.file_url
  );
  const hasAudio = audioItems.length > 0;
  const tracks = collectionItemsToTracks(
    collection.items,
    collection.person.name,
    collection.title
  );

  const handlePlayAll = () => {
    if (tracks.length > 0) playCollection(tracks, 0);
  };

  const handlePlayItem = (item: ContentItemNested, index: number) => {
    if (item.content_type === "audio" && item.file_url) {
      const trackIdx = tracks.findIndex((t) => t.id === item.id);
      if (trackIdx >= 0) {
        playCollection(tracks, trackIdx);
      } else {
        play({
          id: item.id,
          title: item.title,
          personName: collection.person.name,
          fileUrl: item.file_url,
          collectionTitle: collection.title,
        });
      }
    }
  };

  const dur = totalDuration(collection.items);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <button
        onClick={() => router.back()}
        className="text-sm text-saffron-dark font-medium mb-6 hover:text-saffron transition-colors inline-flex items-center gap-1"
      >
        ← Back
      </button>

      {/* Collection header */}
      <div className="bg-gradient-to-br from-brown to-brown-light rounded-2xl p-6 sm:p-8 text-cream mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold mb-3">{collection.title}</h1>
        <div className="flex flex-wrap items-center gap-3 text-cream/70 text-sm">
          <span>{collection.person.name}</span>
          {collection.category && (
            <>
              <span className="text-cream/30">·</span>
              <span>{collection.category.name}</span>
            </>
          )}
          {collection.language && (
            <>
              <span className="text-cream/30">·</span>
              <span>{collection.language.name}</span>
            </>
          )}
          {collection.year && (
            <>
              <span className="text-cream/30">·</span>
              <span>{collection.year}</span>
            </>
          )}
        </div>
        {collection.description && (
          <p className="text-cream/60 text-sm mt-4 leading-relaxed">
            {collection.description}
          </p>
        )}

        <div className="flex items-center gap-4 mt-5">
          {hasAudio && (
            <button
              onClick={handlePlayAll}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-saffron text-brown font-semibold rounded-lg hover:bg-saffron-dark transition-colors"
            >
              ▶ Play All
            </button>
          )}
          <span className="text-xs text-cream/50">
            {collection.items.length} item{collection.items.length !== 1 && "s"}
            {dur && ` · ${dur}`}
          </span>
        </div>
      </div>

      {/* Items list */}
      {collection.items.length === 0 ? (
        <p className="text-center text-warm-gray py-10">
          No items in this collection yet.
        </p>
      ) : (
        <div className="space-y-1">
          {collection.items.map((item, idx) => {
            const isCurrentlyPlaying =
              currentTrack?.id === item.id && isPlaying;

            return (
              <div
                key={item.id}
                className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-colors ${
                  currentTrack?.id === item.id
                    ? "bg-saffron/10 border border-saffron/20"
                    : "hover:bg-cream/50 border border-transparent"
                }`}
              >
                <span className="w-8 text-center text-sm text-warm-gray tabular-nums">
                  {item.chapter_number ?? idx + 1}
                </span>

                {item.content_type === "audio" && item.file_url ? (
                  <button
                    onClick={() => handlePlayItem(item, idx)}
                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-colors ${
                      isCurrentlyPlaying
                        ? "bg-saffron text-brown"
                        : "bg-cream text-brown hover:bg-saffron hover:text-white"
                    }`}
                  >
                    {isCurrentlyPlaying ? (
                      <svg width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                        <rect x="3" y="2" width="4" height="12" rx="1" />
                        <rect x="9" y="2" width="4" height="12" rx="1" />
                      </svg>
                    ) : (
                      <svg width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M4 2l10 6-10 6V2z" />
                      </svg>
                    )}
                  </button>
                ) : (
                  <Link
                    href={`/content/${item.id}`}
                    className="w-8 h-8 rounded-full bg-cream text-brown flex items-center justify-center shrink-0 hover:bg-gold-light transition-colors"
                  >
                    {item.content_type === "pdf" ? "📄" : item.content_type === "video" ? "🎬" : "🔗"}
                  </Link>
                )}

                <div className="flex-1 min-w-0">
                  {item.content_type === "audio" ? (
                    <button
                      onClick={() => handlePlayItem(item, idx)}
                      className="text-sm font-medium text-brown text-left truncate block w-full hover:text-saffron-dark transition-colors"
                    >
                      {item.title}
                    </button>
                  ) : (
                    <Link
                      href={`/content/${item.id}`}
                      className="text-sm font-medium text-brown truncate block hover:text-saffron-dark transition-colors"
                    >
                      {item.title}
                    </Link>
                  )}
                </div>

                <span className="text-xs text-warm-gray tabular-nums shrink-0">
                  {formatDuration(item.duration_seconds)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
