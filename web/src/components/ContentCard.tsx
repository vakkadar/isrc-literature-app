import Link from "next/link";
import type { ContentItem } from "@/types";

function formatDuration(seconds: number | null): string {
  if (!seconds) return "";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function formatSize(bytes: number | null): string {
  if (!bytes) return "";
  const mb = bytes / (1024 * 1024);
  return mb >= 1 ? `${mb.toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`;
}

export default function ContentCard({ item }: { item: ContentItem }) {
  return (
    <Link href={`/content/${item.id}`}>
      <div className="bg-white rounded-xl p-5 shadow-sm border border-[#e0ddd9] hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-semibold text-[#2d2d2d] leading-snug flex-1 mr-3">
            {item.title}
          </h3>
          <span className="shrink-0 text-[11px] font-semibold px-2.5 py-1 rounded bg-blue-50 text-blue-700">
            {item.content_type.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-sm text-[#666] mb-2">
          <span>{item.author_name}</span>
          <span className="text-[#ccc]">·</span>
          <span>{item.subject_name}</span>
          {item.year && (
            <>
              <span className="text-[#ccc]">·</span>
              <span>{item.year}</span>
            </>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex gap-1.5 flex-wrap">
            {item.tags.slice(0, 4).map((tag) => (
              <span
                key={tag.id}
                className="text-[11px] font-medium px-2 py-0.5 rounded bg-[#ede8e3] text-[#4a2c2a]"
              >
                {tag.name}
              </span>
            ))}
          </div>
          <div className="flex gap-3 text-xs text-[#999]">
            {item.duration_seconds ? <span>{formatDuration(item.duration_seconds)}</span> : null}
            {item.file_size_bytes ? <span>{formatSize(item.file_size_bytes)}</span> : null}
          </div>
        </div>

        {item.description && (
          <p className="text-sm text-[#888] mt-2 line-clamp-2">{item.description}</p>
        )}
      </div>
    </Link>
  );
}
