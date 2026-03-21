"use client";

import Link from "next/link";
import type { ContentItem } from "@/types";

function formatDuration(seconds: number | null): string {
  if (!seconds) return "";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m} min`;
}

function formatSize(bytes: number | null): string {
  if (!bytes) return "";
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
}

const TYPE_ICONS: Record<string, { icon: string; color: string; bg: string }> = {
  pdf: { icon: "📄", color: "text-red-700", bg: "bg-red-50" },
  audio: { icon: "🎧", color: "text-saffron-dark", bg: "bg-orange-50" },
  video: { icon: "🎬", color: "text-blue-700", bg: "bg-blue-50" },
  image: { icon: "🖼️", color: "text-green-700", bg: "bg-green-50" },
  link: { icon: "🔗", color: "text-purple-700", bg: "bg-purple-50" },
};

export default function ContentCard({ item }: { item: ContentItem }) {
  const typeInfo = TYPE_ICONS[item.content_type] || TYPE_ICONS.link;
  const href = item.collection
    ? `/collections/${item.collection}`
    : `/content/${item.id}`;

  return (
    <Link href={href} className="block group">
      <div className="bg-white rounded-xl p-5 border border-cream-dark hover:border-gold-light hover:shadow-md transition-all">
        <div className="flex gap-4">
          <div
            className={`w-12 h-12 rounded-lg ${typeInfo.bg} flex items-center justify-center text-xl shrink-0`}
          >
            {typeInfo.icon}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-brown leading-snug group-hover:text-saffron-dark transition-colors line-clamp-2">
              {item.title}
            </h3>
            <div className="flex items-center gap-2 mt-1.5 text-sm text-warm-gray">
              <span>{item.person_name}</span>
              {item.category_name && (
                <>
                  <span className="text-gold-light">·</span>
                  <span>{item.category_name}</span>
                </>
              )}
              {item.year && (
                <>
                  <span className="text-gold-light">·</span>
                  <span>{item.year}</span>
                </>
              )}
            </div>
            <div className="flex items-center gap-2 mt-2">
              <span
                className={`text-[11px] font-semibold uppercase px-2 py-0.5 rounded ${typeInfo.bg} ${typeInfo.color}`}
              >
                {item.content_type}
              </span>
              {item.language_code && (
                <span className="text-[11px] font-medium uppercase px-2 py-0.5 rounded bg-cream text-warm-gray">
                  {item.language_code}
                </span>
              )}
              {item.collection_title && (
                <span className="text-[11px] text-gold truncate max-w-48">
                  {item.collection_title}
                </span>
              )}
              <span className="flex-1" />
              {item.duration_seconds ? (
                <span className="text-xs text-warm-gray">
                  {formatDuration(item.duration_seconds)}
                </span>
              ) : null}
              {item.file_size_bytes ? (
                <span className="text-xs text-warm-gray">
                  {formatSize(item.file_size_bytes)}
                </span>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
