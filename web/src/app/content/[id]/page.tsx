"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Header from "@/components/Header";
import AudioPlayer from "@/components/AudioPlayer";
import { getContentDetail } from "@/services/api";
import type { ContentItemDetail } from "@/types";

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

export default function ContentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [item, setItem] = useState<ContentItemDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("auth_token")) {
      router.replace("/login");
      return;
    }
    const id = Number(params.id);
    getContentDetail(id)
      .then(setItem)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [params.id, router]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="flex justify-center py-20">
          <div className="w-8 h-8 border-3 border-[#4a2c2a] border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="min-h-screen">
        <Header />
        <p className="text-center text-red-600 py-20">Content not found.</p>
      </div>
    );
  }

  const meta = [
    { label: "Author", value: item.author.name },
    { label: "Subject", value: item.subject.name },
    { label: "Year", value: item.year ? String(item.year) : "—" },
    { label: "Type", value: item.content_type.toUpperCase() },
    { label: "Duration", value: formatDuration(item.duration_seconds) },
    { label: "Size", value: formatSize(item.file_size_bytes) },
  ];

  return (
    <div className="min-h-screen">
      <Header />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <button
          onClick={() => router.back()}
          className="text-sm text-[#7b4a3a] font-medium mb-4 hover:text-[#4a2c2a] transition-colors"
        >
          ← Back to Library
        </button>

        <h1 className="text-2xl font-bold mb-6">{item.title}</h1>

        {/* Metadata table */}
        <div className="bg-white rounded-xl border border-[#e0ddd9] divide-y divide-[#e0ddd9] mb-5">
          {meta.map((m) => (
            <div key={m.label} className="flex justify-between px-5 py-3">
              <span className="text-sm text-[#666]">{m.label}</span>
              <span className="text-sm font-medium">{m.value}</span>
            </div>
          ))}
        </div>

        {/* Tags */}
        {item.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-5">
            {item.tags.map((tag) => (
              <span
                key={tag.id}
                className="text-xs font-medium px-3 py-1 rounded-md bg-[#ede8e3] text-[#4a2c2a]"
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}

        {/* Description */}
        {item.description && (
          <p className="text-sm text-[#666] leading-relaxed mb-6">{item.description}</p>
        )}

        {/* Audio player */}
        {item.content_type === "audio" && (
          <AudioPlayer src={item.drive_url} title={item.title} />
        )}
      </main>
    </div>
  );
}
