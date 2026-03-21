"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import ContentCard from "@/components/ContentCard";
import { getContentList, getAuthors, getSubjects, type ContentFilters } from "@/services/api";
import type { ContentItem, Author, Subject } from "@/types";

export default function LibraryPage() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [authors, setAuthors] = useState<Author[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selAuthor, setSelAuthor] = useState<number | undefined>();
  const [selSubject, setSelSubject] = useState<number | undefined>();
  const [selType, setSelType] = useState<string | undefined>();
  const [showFilters, setShowFilters] = useState(false);
  const [count, setCount] = useState(0);
  const router = useRouter();

  useEffect(() => {
    if (!localStorage.getItem("auth_token")) {
      router.replace("/login");
      return;
    }
    Promise.all([getAuthors(), getSubjects()])
      .then(([a, s]) => {
        setAuthors(a.results);
        setSubjects(s.results);
      })
      .catch(() => {});
  }, [router]);

  const loadContent = useCallback(async () => {
    setLoading(true);
    try {
      const filters: ContentFilters = {};
      if (search.trim()) filters.search = search.trim();
      if (selAuthor) filters.author = selAuthor;
      if (selSubject) filters.subject = selSubject;
      if (selType) filters.content_type = selType;
      const data = await getContentList(filters);
      setItems(data.results);
      setCount(data.count);
    } catch {
    } finally {
      setLoading(false);
    }
  }, [search, selAuthor, selSubject, selType]);

  useEffect(() => {
    const t = setTimeout(loadContent, 300);
    return () => clearTimeout(t);
  }, [loadContent]);

  const hasFilters = selAuthor || selSubject || selType || search;

  const clearFilters = () => {
    setSelAuthor(undefined);
    setSelSubject(undefined);
    setSelType(undefined);
    setSearch("");
  };

  return (
    <div className="min-h-screen">
      <Header />

      <main className="max-w-5xl mx-auto px-4 py-6">
        {/* Search + Filter toggle */}
        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search title, author, subject, tags..."
            className="flex-1 px-4 py-2.5 bg-white border border-[#e0ddd9] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#4a2c2a]/20 focus:border-[#4a2c2a]"
          />
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold border transition-colors ${
              showFilters
                ? "bg-[#4a2c2a] text-white border-[#4a2c2a]"
                : "bg-white text-[#2d2d2d] border-[#e0ddd9] hover:border-[#4a2c2a]"
            }`}
          >
            Filters
          </button>
        </div>

        {/* Filter panel */}
        {showFilters && (
          <div className="bg-white border border-[#e0ddd9] rounded-xl p-5 mb-4 space-y-4">
            <FilterSection label="Author">
              {authors.map((a) => (
                <Chip
                  key={a.id}
                  label={a.name}
                  active={selAuthor === a.id}
                  onClick={() => setSelAuthor(selAuthor === a.id ? undefined : a.id)}
                />
              ))}
            </FilterSection>
            <FilterSection label="Subject">
              {subjects.map((s) => (
                <Chip
                  key={s.id}
                  label={s.name}
                  active={selSubject === s.id}
                  onClick={() => setSelSubject(selSubject === s.id ? undefined : s.id)}
                />
              ))}
            </FilterSection>
            <FilterSection label="Type">
              {["audio", "pdf"].map((t) => (
                <Chip
                  key={t}
                  label={t.toUpperCase()}
                  active={selType === t}
                  onClick={() => setSelType(selType === t ? undefined : t)}
                />
              ))}
            </FilterSection>
            {hasFilters && (
              <button onClick={clearFilters} className="text-sm text-red-600 font-medium">
                Clear all filters
              </button>
            )}
          </div>
        )}

        {/* Results count */}
        {!loading && (
          <p className="text-xs text-[#999] mb-3">{count} item{count !== 1 && "s"} found</p>
        )}

        {/* Content list */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-3 border-[#4a2c2a] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : items.length === 0 ? (
          <p className="text-center text-[#999] py-20">No content found.</p>
        ) : (
          <div className="grid gap-3">
            {items.map((item) => (
              <ContentCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function FilterSection({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="text-[11px] font-semibold text-[#666] uppercase tracking-wider mb-2">
        {label}
      </p>
      <div className="flex flex-wrap gap-2">{children}</div>
    </div>
  );
}

function Chip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
        active
          ? "bg-[#4a2c2a] text-white"
          : "bg-[#ede8e3] text-[#4a2c2a] hover:bg-[#ddd7d0]"
      }`}
    >
      {label}
    </button>
  );
}
