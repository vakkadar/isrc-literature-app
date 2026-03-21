"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { useAudio } from "@/contexts/AudioContext";
import { getContentItem, getContentItems } from "@/services/api";
import type { ContentItemDetail, ContentItem } from "@/types";

function formatDuration(seconds: number | null): string {
  if (!seconds) return "—";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m ${s}s`;
  return `${m}m ${s}s`;
}

function formatSize(bytes: number | null): string {
  if (!bytes) return "—";
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
}

function isYouTubeUrl(url: string): string | null {
  const match = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
  );
  return match ? match[1] : null;
}

export default function ContentDetailPage() {
  const { loading: authLoading } = useAuth();
  const params = useParams();
  const router = useRouter();
  const { play, currentTrack, isPlaying, togglePlay } = useAudio();

  const [item, setItem] = useState<ContentItemDetail | null>(null);
  const [related, setRelated] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    const id = Number(params.id);
    getContentItem(id)
      .then((data) => {
        setItem(data);
        const relFilters: Record<string, string | number | undefined> = {
          person: data.person.id,
        };
        if (data.category) relFilters.category = data.category.id;
        return getContentItems(relFilters);
      })
      .then((res) => {
        setRelated(res.results.filter((r) => r.id !== id).slice(0, 6));
      })
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

  if (!item) {
    return (
      <div className="text-center py-20">
        <div className="text-4xl mb-3">😕</div>
        <p className="text-warm-gray">Content not found.</p>
        <button
          onClick={() => router.back()}
          className="mt-4 text-sm text-saffron-dark font-medium hover:text-saffron"
        >
          ← Go back
        </button>
      </div>
    );
  }

  const isCurrentTrack = currentTrack?.id === item.id;
  const ytId = item.external_url ? isYouTubeUrl(item.external_url) : null;

  const handlePlay = () => {
    if (isCurrentTrack) {
      togglePlay();
    } else if (item.file_url) {
      play({
        id: item.id,
        title: item.title,
        personName: item.person.name,
        fileUrl: item.file_url,
        collectionTitle: item.collection?.title,
      });
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
      <button
        onClick={() => router.back()}
        className="text-sm text-saffron-dark font-medium mb-6 hover:text-saffron transition-colors inline-flex items-center gap-1"
      >
        ← Back
      </button>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2">
          <h1 className="text-2xl sm:text-3xl font-bold text-brown mb-4">
            {item.title}
          </h1>

          <div className="flex flex-wrap items-center gap-2 mb-6">
            <span className="text-sm text-warm-gray">{item.person.name}</span>
            {item.category && (
              <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-saffron/10 text-saffron-dark">
                {item.category.name}
              </span>
            )}
            {item.language && (
              <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-cream text-warm-gray uppercase">
                {item.language.code}
              </span>
            )}
            {item.tags.map((tag) => (
              <span
                key={tag.id}
                className="text-xs font-medium px-2.5 py-1 rounded-full bg-gold/10 text-gold"
              >
                {tag.name}
              </span>
            ))}
          </div>

          {item.description && (
            <p className="text-sm text-warm-gray leading-relaxed mb-6">
              {item.description}
            </p>
          )}

          {/* Audio player */}
          {item.content_type === "audio" && item.file_url && (
            <div className="bg-gradient-to-br from-brown to-brown-light rounded-2xl p-6 text-cream mb-6">
              <div className="flex items-center gap-4">
                <button
                  onClick={handlePlay}
                  className="w-16 h-16 rounded-full bg-saffron text-brown flex items-center justify-center hover:bg-saffron-dark transition-colors shrink-0"
                >
                  {isCurrentTrack && isPlaying ? (
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                      <rect x="3" y="2" width="4" height="12" rx="1" />
                      <rect x="9" y="2" width="4" height="12" rx="1" />
                    </svg>
                  ) : (
                    <svg width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M4 2l10 6-10 6V2z" />
                    </svg>
                  )}
                </button>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold truncate">{item.title}</p>
                  <p className="text-cream/50 text-sm">{item.person.name}</p>
                  <p className="text-cream/40 text-xs mt-1">
                    {formatDuration(item.duration_seconds)}
                    {item.file_size_bytes ? ` · ${formatSize(item.file_size_bytes)}` : ""}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* PDF viewer */}
          {item.content_type === "pdf" && item.file_url && (
            <div className="rounded-2xl overflow-hidden border border-cream-dark mb-6">
              <object
                data={item.file_url}
                type="application/pdf"
                className="w-full h-[70vh]"
              >
                <div className="flex flex-col items-center justify-center py-20 bg-cream">
                  <p className="text-warm-gray mb-4">
                    PDF viewer not supported in your browser.
                  </p>
                  <a
                    href={item.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 bg-saffron text-white rounded-lg text-sm font-medium hover:bg-saffron-dark"
                  >
                    Download PDF
                  </a>
                </div>
              </object>
            </div>
          )}

          {/* Video player */}
          {item.content_type === "video" && ytId && (
            <div className="rounded-2xl overflow-hidden border border-cream-dark mb-6 aspect-video">
              <iframe
                src={`https://www.youtube.com/embed/${ytId}`}
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                title={item.title}
              />
            </div>
          )}
          {item.content_type === "video" && !ytId && item.file_url && (
            <div className="rounded-2xl overflow-hidden border border-cream-dark mb-6">
              <video
                src={item.file_url}
                controls
                className="w-full"
              />
            </div>
          )}

          {/* Action buttons */}
          <div className="flex flex-wrap gap-3 mb-6">
            {item.file_url && (
              <a
                href={item.file_url}
                download
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-cream-dark rounded-lg text-sm font-medium text-brown hover:border-saffron transition-colors"
              >
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M8 2v8m0 0l-3-3m3 3l3-3M2 12v1a1 1 0 001 1h10a1 1 0 001-1v-1" />
                </svg>
                Download
              </a>
            )}
            {item.source_url && (
              <a
                href={item.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-cream-dark rounded-lg text-sm font-medium text-brown hover:border-saffron transition-colors"
              >
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10 2h4v4M6 10l8-8M14 8v5a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1h5" />
                </svg>
                Source
              </a>
            )}
            {item.external_url && !ytId && (
              <a
                href={item.external_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-cream-dark rounded-lg text-sm font-medium text-brown hover:border-saffron transition-colors"
              >
                External Link
              </a>
            )}
            {item.collection && (
              <Link
                href={`/collections/${item.collection.id}`}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-saffron/10 border border-saffron/20 rounded-lg text-sm font-medium text-saffron-dark hover:bg-saffron/20 transition-colors"
              >
                📚 View Collection: {item.collection.title}
              </Link>
            )}
          </div>
        </div>

        {/* Sidebar: metadata + related */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-cream-dark divide-y divide-cream-dark">
            {[
              { label: "Person", value: item.person.name },
              { label: "Category", value: item.category?.name || "—" },
              { label: "Language", value: item.language?.name || "—" },
              { label: "Year", value: item.year ? String(item.year) : "—" },
              { label: "Type", value: item.content_type.toUpperCase() },
              { label: "Duration", value: formatDuration(item.duration_seconds) },
              { label: "Size", value: formatSize(item.file_size_bytes) },
              { label: "Chapter", value: item.chapter_number ? String(item.chapter_number) : "—" },
            ].map((m) => (
              <div key={m.label} className="flex justify-between px-4 py-3">
                <span className="text-xs text-warm-gray">{m.label}</span>
                <span className="text-xs font-medium text-brown text-right">
                  {m.value}
                </span>
              </div>
            ))}
          </div>

          {related.length > 0 && (
            <div>
              <h3 className="text-sm font-bold text-brown mb-3">Related</h3>
              <div className="space-y-2">
                {related.map((r) => (
                  <Link
                    key={r.id}
                    href={
                      r.collection
                        ? `/collections/${r.collection}`
                        : `/content/${r.id}`
                    }
                    className="block bg-white rounded-lg p-3 border border-cream-dark hover:border-saffron/30 transition-colors"
                  >
                    <p className="text-xs font-medium text-brown line-clamp-2">
                      {r.title}
                    </p>
                    <p className="text-[10px] text-warm-gray mt-1">
                      {r.person_name} · {r.content_type.toUpperCase()}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
