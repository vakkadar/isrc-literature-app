"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { getCategories, getContentItems } from "@/services/api";
import type { Category, ContentItem } from "@/types";

const CATEGORY_ICONS: Record<string, string> = {
  books: "📚",
  "audio-books": "🎧",
  speeches: "🎤",
  letters: "✉️",
  articles: "📰",
  videos: "🎬",
  images: "🖼️",
  messages: "💬",
};

function getIconForCategory(slug: string, icon: string): string {
  if (icon) return icon;
  return CATEGORY_ICONS[slug] || "📂";
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return "";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m} min`;
}

export default function HomePage() {
  const { loading: authLoading } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [recentItems, setRecentItems] = useState<ContentItem[]>([]);
  const [stats, setStats] = useState({ total: 0, audio: 0, pdf: 0, video: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    Promise.all([
      getCategories(),
      getContentItems({ ordering: "-created_at", page: 1 }),
      getContentItems({ content_type: "audio" }),
      getContentItems({ content_type: "pdf" }),
      getContentItems({ content_type: "video" }),
    ])
      .then(([cats, recent, audioRes, pdfRes, videoRes]) => {
        setCategories(cats.results);
        setRecentItems(recent.results.slice(0, 6));
        setStats({
          total: recent.count,
          audio: audioRes.count,
          pdf: pdfRes.count,
          video: videoRes.count,
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [authLoading]);

  if (loading || authLoading) {
    return (
      <div className="flex justify-center py-32">
        <div className="w-8 h-8 border-3 border-saffron border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <section className="relative overflow-hidden bg-gradient-to-br from-brown via-brown-light to-brown py-20 text-cream">
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-10 left-10 text-[200px] leading-none">🪷</div>
          <div className="absolute bottom-0 right-10 text-[150px] leading-none">ॐ</div>
        </div>
        <div className="relative max-w-5xl mx-auto px-4 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 tracking-tight">
            Digital Library of
            <br />
            <span className="text-saffron">Sahaj Marg Literature</span>
          </h1>
          <p className="text-cream/60 text-lg max-w-2xl mx-auto">
            Explore the spiritual teachings through books, audio recordings, letters, and more.
          </p>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 -mt-8">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Total Items", value: stats.total, icon: "📊" },
            { label: "Books & PDFs", value: stats.pdf, icon: "📚" },
            { label: "Audio Files", value: stats.audio, icon: "🎧" },
            { label: "Videos", value: stats.video, icon: "🎬" },
          ].map((s) => (
            <div
              key={s.label}
              className="bg-white rounded-xl p-5 border border-cream-dark shadow-sm text-center"
            >
              <div className="text-2xl mb-1">{s.icon}</div>
              <div className="text-2xl font-bold text-brown">{s.value}</div>
              <div className="text-xs text-warm-gray mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {categories.length > 0 && (
        <section className="max-w-5xl mx-auto px-4 mt-12">
          <h2 className="text-xl font-bold text-brown mb-5">Browse by Category</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {categories.map((cat) => (
              <Link
                key={cat.id}
                href={`/library?category=${cat.id}`}
                className="group bg-white rounded-xl p-5 border border-cream-dark hover:border-saffron/30 hover:shadow-md transition-all text-center"
              >
                <div className="text-3xl mb-2">
                  {getIconForCategory(cat.slug, cat.icon)}
                </div>
                <div className="font-semibold text-brown text-sm group-hover:text-saffron-dark transition-colors">
                  {cat.name}
                </div>
                {cat.description && (
                  <p className="text-xs text-warm-gray mt-1 line-clamp-2">
                    {cat.description}
                  </p>
                )}
              </Link>
            ))}
          </div>
        </section>
      )}

      {recentItems.length > 0 && (
        <section className="max-w-5xl mx-auto px-4 mt-12 pb-12">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xl font-bold text-brown">Recently Added</h2>
            <Link
              href="/library?ordering=-created_at"
              className="text-sm text-saffron-dark font-medium hover:text-saffron transition-colors"
            >
              View all →
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentItems.map((item) => (
              <Link
                key={item.id}
                href={
                  item.collection
                    ? `/collections/${item.collection}`
                    : `/content/${item.id}`
                }
                className="group bg-white rounded-xl p-5 border border-cream-dark hover:border-saffron/30 hover:shadow-md transition-all"
              >
                <div className="flex items-start gap-3">
                  <div className="text-xl shrink-0">
                    {item.content_type === "audio"
                      ? "🎧"
                      : item.content_type === "video"
                        ? "🎬"
                        : "📄"}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-brown text-sm group-hover:text-saffron-dark transition-colors line-clamp-2">
                      {item.title}
                    </h3>
                    <p className="text-xs text-warm-gray mt-1">
                      {item.person_name}
                      {item.year && ` · ${item.year}`}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-cream text-warm-gray">
                        {item.content_type}
                      </span>
                      {item.duration_seconds ? (
                        <span className="text-[10px] text-warm-gray">
                          {formatDuration(item.duration_seconds)}
                        </span>
                      ) : null}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
